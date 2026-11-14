"""Metrics, cost-based threshold selection, calibration and plots."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from src.config import COST_FN, COST_FP, REPORTS

def metrics_at(y, proba, thr):
    pred = (proba >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "threshold": round(float(thr), 4),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "roc_auc": roc_auc_score(y, proba) if len(set(proba)) > 1 else 0.5,
        "pr_auc": average_precision_score(y, proba),
        "brier": brier_score_loss(y, np.clip(proba, 0, 1)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "expected_cost": float(fn * COST_FN + fp * COST_FP),
    }

def cost_curve(y, proba, grid=None):
    grid = np.linspace(0.02, 0.9, 89) if grid is None else grid
    rows = [metrics_at(y, proba, t) for t in grid]
    return pd.DataFrame(rows)

def best_threshold(y, proba):
    """Threshold that minimises expected business cost on VALIDATION data."""
    c = cost_curve(y, proba)
    return float(c.loc[c["expected_cost"].idxmin(), "threshold"])

def plot_threshold(curve, thr, path):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(curve["threshold"], curve["precision"], label="precision")
    ax[0].plot(curve["threshold"], curve["recall"], label="recall")
    ax[0].plot(curve["threshold"], curve["f1"], label="F1")
    ax[0].axvline(thr, ls="--", c="k", label=f"chosen = {thr:.2f}")
    ax[0].set_xlabel("threshold"); ax[0].legend(); ax[0].set_title("Precision / recall vs threshold")
    ax[1].plot(curve["threshold"], curve["expected_cost"], c="C3")
    ax[1].axvline(thr, ls="--", c="k")
    ax[1].set_xlabel("threshold"); ax[1].set_title(f"Expected cost (FN={COST_FN:g}, FP={COST_FP:g})")
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)

def plot_calibration(curves: dict, path):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], "k--", label="perfect")
    for name, (y, p) in curves.items():
        frac, mean = calibration_curve(y, p, n_bins=10, strategy="quantile")
        ax.plot(mean, frac, marker="o", label=name)
    ax.set_xlabel("mean predicted probability"); ax.set_ylabel("observed no-show rate")
    ax.legend(); ax.set_title("Calibration (test set)")
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)

def plot_confusion(m, path, title):
    cm = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=14)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["pred attend", "pred no-show"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["attended", "no-show"]); ax.set_title(title)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)

def fairness_table(df, y, proba, thr, group_col):
    rows = []
    for g, idx in df.groupby(group_col).groups.items():
        yy, pp = y.loc[idx], proba[df.index.get_indexer(idx)]
        m = metrics_at(yy, pp, thr)
        rows.append({group_col: g, "n": len(yy), "no_show_rate": yy.mean(),
                     "flag_rate": (pp >= thr).mean(), "precision": m["precision"], "recall": m["recall"]})
    return pd.DataFrame(rows)

