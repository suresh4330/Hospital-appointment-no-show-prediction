"""End-to-end, reproducible training:  python -m src.train
data -> chronological split -> baselines -> 4 models -> tuning (validation only)
-> calibration -> cost-based threshold (validation) -> ONE final test evaluation -> save."""
import itertools
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from src import evaluate as ev
from src.config import (AUDIT_COLS, CATEGORICAL, DATA_PATH, META_PATH, MODEL_PATH, NUMERIC,
                        REPORTS, SEED, TARGET, COST_FN, COST_FP)
from src.features import add_features, build_preprocessor
from src.generate_data import generate

FEATURES = NUMERIC + CATEGORICAL

def load_data():
    if not DATA_PATH.exists():
        DATA_PATH.parent.mkdir(exist_ok=True)
        generate().to_csv(DATA_PATH, index=False)
    df = pd.read_csv(DATA_PATH, parse_dates=["booking_date", "appointment_date"])
    return add_features(df).sort_values("appointment_date").reset_index(drop=True)

def chrono_split(df, tr=0.70, va=0.15):
    n = len(df)
    a, b = int(n * tr), int(n * (tr + va))
    return df.iloc[:a].copy(), df.iloc[a:b].copy(), df.iloc[b:].copy()

def make_pipe(est):
    return Pipeline([("prep", build_preprocessor()), ("clf", est)])

class RuleBaseline:
    """Simple business rule: flag long lead time OR repeat no-shower."""
    def predict_proba(self, X):
        s = ((X["lead_time_days"] >= 21) | (X["prev_no_shows"] >= 2)).astype(float).values
        return np.c_[1 - s, s]

def main():
    REPORTS.mkdir(exist_ok=True)
    df = load_data()
    train, val, test = chrono_split(df)
    print(f"rows: train={len(train)} val={len(val)} test={len(test)} | "
          f"no-show rate train={train[TARGET].mean():.1%} test={test[TARGET].mean():.1%}")
    print(f"train {train.appointment_date.min().date()}..{train.appointment_date.max().date()} | "
          f"test {test.appointment_date.min().date()}..{test.appointment_date.max().date()}")
    Xtr, ytr = train[FEATURES], train[TARGET]
    Xva, yva = val[FEATURES], val[TARGET]
    Xte, yte = test[FEATURES], test[TARGET]

    # Calculate class imbalance ratio for XGBoost scale_pos_weight
    scale_pos = float((ytr == 0).sum() / (ytr == 1).sum())

    # ---------- candidates (class imbalance handled with class weights) ----------
    models = {
        "dummy_prior": make_pipe(DummyClassifier(strategy="prior")),
        "logreg": make_pipe(LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED)),
        "random_forest": make_pipe(RandomForestClassifier(
            n_estimators=300, min_samples_leaf=20, class_weight="balanced_subsample",
            n_jobs=-1, random_state=SEED)),
        "xgboost": make_pipe(XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            scale_pos_weight=scale_pos, eval_metric="aucpr", random_state=SEED)),
    }
    # small, explainable grid search for the boosting model, scored on VALIDATION PR-AUC
    best, best_score, grid_log = None, -1, []
    for lr, depth, leaf in itertools.product([0.05, 0.1], [3, 5], [20, 50]):
        est = HistGradientBoostingClassifier(learning_rate=lr, max_depth=depth, min_samples_leaf=leaf,
                                             max_iter=200, class_weight="balanced", random_state=SEED)
        p = make_pipe(est).fit(Xtr, ytr)
        s = average_precision_score(yva, p.predict_proba(Xva)[:, 1])
        grid_log.append({"learning_rate": lr, "max_depth": depth,
                         "min_samples_leaf": leaf, "val_pr_auc": round(s, 4)})
        if s > best_score:
            best, best_score = est, s
    pd.DataFrame(grid_log).to_csv(REPORTS / "tuning_log.csv", index=False)
    models["grad_boosting"] = make_pipe(best)
    fitted = {k: m.fit(Xtr, ytr) for k, m in models.items()}

    # ---------- compare on VALIDATION (threshold chosen per model by cost) ----------
    rows, thr_by = [], {}
    rule = RuleBaseline()
    pv = rule.predict_proba(Xva)[:, 1]
    rows.append({"model": "rule_baseline", **ev.metrics_at(yva, pv, 0.5), "split": "validation"})
    rows.append({"model": "flag_everyone", **ev.metrics_at(yva, np.ones(len(yva)), 0.5),
                 "split": "validation"})
    for name, m in fitted.items():
        pv = m.predict_proba(Xva)[:, 1]
        thr_by[name] = 0.5 if name == "dummy_prior" else ev.best_threshold(yva, pv)
        rows.append({"model": name, **ev.metrics_at(yva, pv, thr_by[name]), "split": "validation"})
    val_tbl = pd.DataFrame(rows)
    cand = val_tbl[~val_tbl["model"].isin(["rule_baseline", "dummy_prior", "flag_everyone"])]
    winner = cand.loc[cand["pr_auc"].idxmax(), "model"]
    show = ["model", "precision", "recall", "f1", "pr_auc", "brier", "expected_cost"]
    print("\nValidation comparison:\n", val_tbl[show].round(3).to_string(index=False))
    print(f"\nSelected model (best validation PR-AUC): {winner}")

    # ---------- calibration (class weights distort probabilities) ----------
    raw = fitted[winner]
    cal = CalibratedClassifierCV(clone(models[winner]), method="isotonic", cv=3).fit(Xtr, ytr)
    b_raw = brier_score_loss(yva, raw.predict_proba(Xva)[:, 1])
    b_cal = brier_score_loss(yva, cal.predict_proba(Xva)[:, 1])
    final = cal if b_cal < b_raw else raw
    final_name = f"{winner}+isotonic" if final is cal else winner
    print(f"Brier on validation: raw={b_raw:.4f} calibrated={b_cal:.4f} -> using {final_name}")
    thr = ev.best_threshold(yva, final.predict_proba(Xva)[:, 1])
    print(f"Cost-optimal threshold (validation): {thr:.2f}")
    pva = final.predict_proba(Xva)[:, 1]
    ev.plot_threshold(ev.cost_curve(yva, pva), thr, REPORTS / "threshold_curve.png")

    # ---------- FINAL held-out TEST evaluation (used once) ----------
    trows = [{"model": "rule_baseline", **ev.metrics_at(yte, rule.predict_proba(Xte)[:, 1], 0.5)},
             {"model": "flag_everyone", **ev.metrics_at(yte, np.ones(len(yte)), 0.5)}]
    for name, m in fitted.items():
        trows.append({"model": name, **ev.metrics_at(yte, m.predict_proba(Xte)[:, 1], thr_by[name])})
    pte = final.predict_proba(Xte)[:, 1]
    trows.append({"model": f"FINAL: {final_name}", **ev.metrics_at(yte, pte, thr)})
    test_tbl = pd.DataFrame(trows)
    test_tbl.to_csv(REPORTS / "model_comparison_test.csv", index=False)
    val_tbl.to_csv(REPORTS / "model_comparison_validation.csv", index=False)
    show = ["model", "precision", "recall", "f1", "pr_auc", "brier", "fp", "fn", "expected_cost"]
    print("\nTEST comparison:\n", test_tbl[show].round(3).to_string(index=False))
    final_m = ev.metrics_at(yte, pte, thr)
    ev.plot_confusion(final_m, REPORTS / "confusion_matrix.png", f"Test @ thr={thr:.2f}")
    ev.plot_calibration({"raw model": (yte, raw.predict_proba(Xte)[:, 1]),
                         "final model": (yte, pte)}, REPORTS / "calibration_curve.png")

    # ---------- fairness audit (audit cols are NOT model inputs) ----------
    audit = test.reset_index(drop=True)
    for col in AUDIT_COLS:
        tbl = ev.fairness_table(audit, audit[TARGET], pte, thr, col).round(3)
        tbl.to_csv(REPORTS / f"fairness_{col}.csv", index=False)

    # ---------- global importance ----------
    imp = permutation_importance(final, Xte, yte, scoring="average_precision",
                                 n_repeats=5, random_state=SEED, n_jobs=1)
    pd.DataFrame({"feature": FEATURES, "importance": imp.importances_mean}).sort_values(
        "importance", ascending=False).to_csv(REPORTS / "permutation_importance.csv", index=False)

    # ---------- save artifact ----------
    reference = {c: Xtr[c].median() for c in NUMERIC}
    reference.update({c: Xtr[c].mode().iloc[0] for c in CATEGORICAL})
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"model": final, "threshold": thr, "reference": reference,
                 "features": FEATURES}, MODEL_PATH)
    meta = {
        "model": final_name,
        "threshold": thr,
        "seed": SEED,
        "cost_fn": COST_FN,
        "cost_fp": COST_FP,
        "n_train": len(train),
        "n_val": len(val),
        "n_test": len(test),
        "n_no_show_train": int(train[TARGET].sum()),
        "n_no_show_val": int(val[TARGET].sum()),
        "n_no_show_test": int(test[TARGET].sum()),
        "brier_val_raw": round(float(b_raw), 4),
        "brier_val_calibrated": round(float(b_cal), 4),
        "test_metrics": final_m,
        "prediction_time": "when the appointment is booked",
    }
    META_PATH.write_text(json.dumps(meta, indent=2, default=float))
    print(f"\nSaved {MODEL_PATH.name}, reports/ and model_meta.json")

if __name__ == "__main__":
    main()
