import pandas as pd
from src.generate_data import generate
from src.train import chrono_split
from src.features import add_features

def test_generator_is_reproducible():
    a, b = generate(300, 800, seed=1), generate(300, 800, seed=1)
    pd.testing.assert_frame_equal(a, b)

def test_chronological_split_has_no_time_overlap():
    df = add_features(generate(300, 1000, seed=3)).sort_values("appointment_date").reset_index(drop=True)
    tr, va, te = chrono_split(df)
    assert tr.appointment_date.max() <= va.appointment_date.min()
    assert va.appointment_date.max() <= te.appointment_date.min()

def test_history_features_only_use_past():
    """prev_visits can never exceed the number of this patient's appointments dated before booking."""
    df = generate(200, 800, seed=5)
    for pid, g in list(df.groupby("patient_id"))[:50]:
        for _, r in g.iterrows():
            past = (g["appointment_date"] < r["booking_date"]).sum()
            assert r["prev_visits"] == past
            assert r["prev_no_shows"] <= r["prev_visits"]

