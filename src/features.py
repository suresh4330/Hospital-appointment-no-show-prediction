"""Feature engineering + preprocessing. Used by BOTH training and inference,
so the model can never see differently-prepared data in production."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from src.config import NUMERIC, CATEGORICAL, FORBIDDEN

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive features using ONLY information known when the appointment is booked."""
    d = df.copy()
    # clean impossible values (data-quality step)
    d["age"] = pd.to_numeric(d["age"], errors="coerce")
    d.loc[(d["age"] < 0) | (d["age"] > 110), "age"] = np.nan
    d["lead_time_days"] = pd.to_numeric(d["lead_time_days"], errors="coerce").clip(lower=0)
    d["prev_visits"] = pd.to_numeric(d["prev_visits"], errors="coerce").fillna(0)
    d["prev_no_shows"] = pd.to_numeric(d["prev_no_shows"], errors="coerce").fillna(0)
    d["prev_no_show_rate"] = np.where(d["prev_visits"] > 0,
                                      d["prev_no_shows"] / d["prev_visits"].clip(lower=1), 0.0)
    # New feature 1: absolute count of past attended visits
    d["prev_attended"] = (d["prev_visits"] - d["prev_no_shows"]).clip(lower=0)
    # New feature 2: indicator if this is a first-time patient with no prior visit history
    d["is_first_visit"] = np.where(d["prev_visits"] == 0, "yes", "no")

    d["hour_bucket"] = pd.cut(d["appt_hour"], [0, 9, 12, 15, 24],
                              labels=["early", "late_morning", "afternoon", "late"]).astype(str)
    d["lead_bucket"] = pd.cut(d["lead_time_days"], [-1, 3, 14, 30, 10_000],
                              labels=["0-3d", "4-14d", "15-30d", "30d+"]).astype(str)
    for c in ["appt_weekday", "department", "booking_channel", "reminder_scheduled", "is_follow_up", "is_first_visit"]:
        d[c] = d[c].astype("object").where(d[c].notna(), "unknown").astype(str)
    return d

def assert_no_forbidden(columns) -> None:
    """Leakage guard: raise if any prohibited column is used as a model input."""
    bad = set(columns) & set(FORBIDDEN)
    if bad:
        raise ValueError(f"Forbidden columns used as features: {sorted(bad)}")

def build_preprocessor() -> ColumnTransformer:
    assert_no_forbidden(NUMERIC + CATEGORICAL)
    num = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
    cat = Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="unknown")),
                    ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    return ColumnTransformer([("num", num, NUMERIC), ("cat", cat, CATEGORICAL)])
