"""Cost sensitivity analysis: evaluates how varying (COST_FN, COST_FP) moves the threshold."""
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from src.config import MODEL_PATH, REPORTS, TARGET
from src.train import chrono_split, load_data

PAIRS = [
    (10.0, 2.0),
    (10.0, 1.0),
    (10.0, 5.0),
    (20.0, 2.0),
    (5.0, 2.0),
    (10.0, 10.0),
]

def find_optimal_threshold(y_true, proba, cost_fn, cost_fp, grid=None):
    """Find threshold that minimises expected cost on a dataset."""
    if grid is None:
        grid = np.linspace(0.02, 0.90, 89)
    best_thr, min_cost = 0.5, float("inf")
    for thr in grid:
        pred = (proba >= thr).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
        cost = fn * cost_fn + fp * cost_fp
        if cost < min_cost:
            min_cost = cost
            best_thr = float(thr)
    return round(best_thr, 4)

def main():
    REPORTS.mkdir(exist_ok=True)
    df = load_data()
    _, val, test = chrono_split(df)

    art = joblib.load(MODEL_PATH)
    model = art["model"]
    features = art["features"]

    y_val = val[TARGET].values
    p_val = model.predict_proba(val[features])[:, 1]

    y_test = test[TARGET].values
    p_test = model.predict_proba(test[features])[:, 1]

    rows = []
    for cost_fn, cost_fp in PAIRS:
        ratio = cost_fn / cost_fp
        thr = find_optimal_threshold(y_val, p_val, cost_fn, cost_fp)

        pred_test = (p_test >= thr).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred_test, labels=[0, 1]).ravel()
        prec = precision_score(y_test, pred_test, zero_division=0)
        rec = recall_score(y_test, pred_test, zero_division=0)
        test_cost = fn * cost_fn + fp * cost_fp

        rows.append({
            "cost_fn": cost_fn,
            "cost_fp": cost_fp,
            "ratio_fn_fp": ratio,
            "opt_threshold": thr,
            "test_precision": round(prec, 3),
            "test_recall": round(rec, 3),
            "n_flagged": int(fp + tp),
            "test_fp": int(fp),
            "test_fn": int(fn),
            "expected_cost": round(test_cost, 1),
        })

    res_df = pd.DataFrame(rows)
    out_path = REPORTS / "cost_sensitivity.csv"
    res_df.to_csv(out_path, index=False)

    print("\nCost Sensitivity Analysis (threshold chosen on validation, evaluated on test):")
    print(res_df.to_string(index=False))
    print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    main()

