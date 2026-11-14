"""Inference: loads the SAVED artifact and returns real predictions + explanations."""
import json
import joblib
import numpy as np
import pandas as pd
from src.config import MODEL_PATH, NUMERIC, CATEGORICAL
from src.features import add_features, assert_no_forbidden

_ART = None
INPUT_FIELDS = ["age", "distance_km", "lead_time_days", "appt_weekday", "appt_hour", "department",
                "booking_channel", "reminder_scheduled", "is_follow_up", "prev_visits", "prev_no_shows"]

def load_artifact(path=MODEL_PATH):
    global _ART
    if _ART is None:
        _ART = joblib.load(path)
    return _ART

def _frame(records):
    df = pd.DataFrame(records)
    assert_no_forbidden(df.columns)             # leakage guard at inference time too
    for c in INPUT_FIELDS:
        if c not in df:
            df[c] = np.nan
    return add_features(df)

def risk_band(p, thr):
    if p >= max(thr * 1.6, 0.5):
        return "high"
    return "medium" if p >= thr else "low"

def explain(row_df, art, top_k=4):
    """Occlusion explanation: how much does the probability move if one input is
    replaced by the typical (reference) value? Positive = pushes risk UP."""
    model, ref = art["model"], art["reference"]
    base = float(model.predict_proba(row_df)[0, 1])
    out = []
    for col in NUMERIC + CATEGORICAL:
        alt = row_df.copy()
        alt[col] = ref[col]
        delta = base - float(model.predict_proba(alt)[0, 1])
        out.append((col, row_df[col].iloc[0], delta))
    out.sort(key=lambda t: abs(t[2]), reverse=True)
    return [{"feature": c, "value": (v.item() if hasattr(v, "item") else v),
             "effect": round(d, 4), "direction": "raises risk" if d > 0 else "lowers risk"}
            for c, v, d in out[:top_k]]

def predict_records(records, with_explanation=True):
    art = load_artifact()
    X = _frame(records)
    probs = art["model"].predict_proba(X)[:, 1]
    thr = art["threshold"]
    results = []
    for i, p in enumerate(probs):
        band = risk_band(p, thr)
        res = {
            "no_show_probability": round(float(p), 4),
            "risk_band": band,
            "flagged_for_review": bool(p >= thr),
            "suggested_action": ("Staff may consider a human-reviewed reminder call/SMS"
                                 if p >= thr else "Standard reminder process"),
            "disclaimer": "Decision-support only. Not a clinical prediction. Staff must review.",
        }
        if with_explanation:
            res["top_factors"] = explain(X.iloc[[i]], art)
        results.append(res)
    return results

def predict_one(record, with_explanation=True):
    return predict_records([record], with_explanation)[0]

