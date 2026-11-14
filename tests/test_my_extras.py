"""Additional unit tests verifying new feature engineering and cost monotonicity."""
import numpy as np
import pandas as pd
from src import evaluate
from src.features import add_features

def test_new_features_are_correct_and_leak_free():
    """Verifies prev_attended and is_first_visit computations without mutating inputs."""
    raw = pd.DataFrame({
        "age": [25, 45, 60],
        "distance_km": [5.0, 12.0, 20.0],
        "lead_time_days": [3, 14, 30],
        "appt_weekday": ["Monday", "Wednesday", "Friday"],
        "appt_hour": [9, 11, 14],
        "department": ["General Practice", "Dental", "Eye Clinic"],
        "booking_channel": ["online", "phone", "front_desk"],
        "reminder_scheduled": ["yes", "no", "yes"],
        "is_follow_up": ["no", "yes", "no"],
        "prev_visits": [0, 5, 3],
        "prev_no_shows": [0, 2, 3],
    })
    # Preserve a deep copy of original inputs to test immutability
    original = raw.copy(deep=True)

    # Derive features
    d = add_features(raw)

    # 1. prev_attended equals prev_visits - prev_no_shows and is never negative
    expected_attended = (d["prev_visits"] - d["prev_no_shows"]).clip(lower=0)
    assert (d["prev_attended"] == expected_attended).all()
    assert (d["prev_attended"] >= 0).all()
    assert d["prev_attended"].tolist() == [0, 3, 0]

    # 2. is_first_visit is 'yes' only when prev_visits == 0
    assert (d["is_first_visit"] == "yes").tolist() == [True, False, False]
    assert ((d["is_first_visit"] == "yes") == (d["prev_visits"] == 0)).all()

    # 3. Original DataFrame columns remain intact and unmutated
    pd.testing.assert_frame_equal(raw, original)

def test_raising_fp_cost_never_lowers_threshold(monkeypatch):
    """Asserts that as false-alarm cost increases, the optimal threshold is non-decreasing."""
    rng = np.random.default_rng(42)
    # 200 synthetic outcomes with 20% positive class rate
    y_true = rng.choice([0, 1], size=200, p=[0.8, 0.2])
    proba = rng.uniform(0.0, 1.0, size=200)

    monkeypatch.setattr(evaluate, "COST_FN", 10.0)

    # Test increasing COST_FP from 1.0 to 2.0 to 5.0
    monkeypatch.setattr(evaluate, "COST_FP", 1.0)
    thr_fp1 = evaluate.best_threshold(y_true, proba)

    monkeypatch.setattr(evaluate, "COST_FP", 2.0)
    thr_fp2 = evaluate.best_threshold(y_true, proba)

    monkeypatch.setattr(evaluate, "COST_FP", 5.0)
    thr_fp5 = evaluate.best_threshold(y_true, proba)

    # When reminders get more expensive, threshold must stay equal or rise (never drop)
    assert thr_fp1 <= thr_fp2 <= thr_fp5

