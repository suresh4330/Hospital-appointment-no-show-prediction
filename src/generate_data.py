"""Synthetic hospital appointment generator (no real patient data).
Key design points (explain these in your report):
* Every row is ONE appointment, made at `booking_date`.
* Patient-history features (prev_visits, prev_no_shows) are computed ONLY from
  that patient's earlier appointments whose date is BEFORE this booking date,
  so they are genuinely known at prediction time (no leakage).
* The no-show probability is driven by a hidden per-patient propensity plus
  observable factors, so history is informative but the signal is noisy.
* Fixed seed -> fully reproducible.
"""
import argparse
import numpy as np
import pandas as pd
from src.config import DATA_PATH, SEED

DEPARTMENTS = ["General Practice", "Pediatrics", "Dental", "Eye Clinic", "Physiotherapy"]
CHANNELS = ["phone", "online", "front_desk"]

def generate(n_patients: int = 3000, n_appts: int = 12000, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # ---- patients ----
    pat = pd.DataFrame({
        "patient_id": np.arange(n_patients),
        "age": np.clip(rng.normal(40, 18, n_patients), 1, 95).round().astype(int),
        "gender": rng.choice(["F", "M"], n_patients),
        "distance_km": np.clip(rng.gamma(2.0, 4.0, n_patients), 0.3, 60).round(1),
        "propensity": rng.normal(0, 1, n_patients),   # hidden "forgetfulness"
    })
    # ---- appointments ----
    start = pd.Timestamp("2024-01-01")
    n_days = 540
    idx = rng.integers(0, n_patients, n_appts)
    df = pat.iloc[idx].reset_index(drop=True)
    df.insert(0, "appointment_id", np.arange(n_appts))
    appt_day = rng.integers(0, n_days, n_appts)
    lead = np.clip(rng.gamma(1.6, 8.0, n_appts), 0, 90).round().astype(int)
    df["appointment_date"] = start + pd.to_timedelta(appt_day, unit="D")
    df["booking_date"] = df["appointment_date"] - pd.to_timedelta(lead, unit="D")
    df["lead_time_days"] = lead
    # clinics are closed on weekends: shift Sat/Sun to Monday
    wd = df["appointment_date"].dt.weekday
    df.loc[wd >= 5, "appointment_date"] += pd.to_timedelta(7 - wd[wd >= 5], unit="D")
    df["lead_time_days"] = (df["appointment_date"] - df["booking_date"]).dt.days
    df["appt_weekday"] = df["appointment_date"].dt.day_name()
    df["appt_hour"] = rng.choice(np.arange(8, 17), n_appts,
                                 p=[.14, .14, .13, .11, .08, .09, .11, .11, .09])
    df["department"] = rng.choice(DEPARTMENTS, n_appts, p=[.35, .15, .2, .15, .15])
    df["booking_channel"] = rng.choice(CHANNELS, n_appts, p=[.4, .3, .3])
    df["reminder_scheduled"] = rng.choice(["yes", "no"], n_appts, p=[.6, .4])
    df["is_follow_up"] = rng.choice(["yes", "no"], n_appts, p=[.35, .65])
    # ---- sort by appointment date to build the outcome history ----
    df = df.sort_values("appointment_date").reset_index(drop=True)
    # ---- true no-show process (hidden from the model) ----
    logit = (
        -2.3
        + 0.045 * df["lead_time_days"]
        + 1.25 * df["propensity"]
        + 0.025 * df["distance_km"]
        - 0.9 * (df["reminder_scheduled"] == "yes")
        - 0.5 * (df["booking_channel"] == "online")
        + 0.35 * (df["appt_weekday"] == "Monday")
        + 0.30 * (df["appt_weekday"] == "Friday")
        + 0.25 * (df["appt_hour"].isin([8, 16]))
        - 0.35 * (df["is_follow_up"] == "yes")
        - 0.015 * (df["age"] - 40)
        + 0.30 * (df["department"] == "Dental")
        + rng.normal(0, 0.3, len(df))
    )
    p = 1 / (1 + np.exp(-logit))
    df["no_show"] = (rng.random(len(df)) < p).astype(int)
    # ---- leak-free history features ----
    prev_visits = np.zeros(len(df), dtype=int)
    prev_ns = np.zeros(len(df), dtype=int)
    for _, g in df.groupby("patient_id"):
        dates = g["appointment_date"].values
        outcomes = g["no_show"].values
        pos = g.index.values
        for i, row_idx in enumerate(pos):
            booked = g.loc[row_idx, "booking_date"].to_datetime64()
            mask = dates < booked            # only appts that already happened
            prev_visits[row_idx] = int(mask.sum())
            prev_ns[row_idx] = int(outcomes[mask].sum())
    df["prev_visits"] = prev_visits
    df["prev_no_shows"] = prev_ns
    # ---- tidy / realistic data-quality issues for the EDA step ----
    df["age_group"] = pd.cut(df["age"], [0, 17, 39, 59, 120],
                             labels=["0-17", "18-39", "40-59", "60+"]).astype(str)
    miss = rng.random(len(df))
    df.loc[miss < 0.02, "distance_km"] = np.nan             # ~2% missing
    df.loc[(miss > 0.98), "booking_channel"] = np.nan       # ~2% missing
    out = df.sample(frac=0.003, random_state=seed).index
    df.loc[out, "age"] = df.loc[out, "age"] + 100            # a few impossible ages
    cols = ["appointment_id", "patient_id", "booking_date", "appointment_date",
            "age", "gender", "age_group", "distance_km", "lead_time_days",
            "appt_weekday", "appt_hour", "department", "booking_channel",
            "reminder_scheduled", "is_follow_up", "prev_visits", "prev_no_shows", "no_show"]
    return df[cols]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_appts", type=int, default=12000)
    ap.add_argument("--n_patients", type=int, default=3000)
    a = ap.parse_args()
    data = generate(a.n_patients, a.n_appts)
    DATA_PATH.parent.mkdir(exist_ok=True)
    data.to_csv(DATA_PATH, index=False)
    print(f"Saved {len(data)} rows -> {DATA_PATH}; no-show rate = {data['no_show'].mean():.1%}")

