import numpy as np
import pandas as pd
import pytest
from src.config import NUMERIC, CATEGORICAL, FORBIDDEN
from src.features import add_features, assert_no_forbidden, build_preprocessor

def _row(**kw):
    base = dict(age=30, distance_km=5.0, lead_time_days=10, appt_weekday="Monday", appt_hour=9,
                department="Dental", booking_channel="phone", reminder_scheduled="yes",
                is_follow_up="no", prev_visits=4, prev_no_shows=1)
    base.update(kw)
    return pd.DataFrame([base])

def test_prev_no_show_rate():
    d = add_features(_row(prev_visits=4, prev_no_shows=1))
    assert d["prev_no_show_rate"].iloc[0] == pytest.approx(0.25)
    assert add_features(_row(prev_visits=0, prev_no_shows=0))["prev_no_show_rate"].iloc[0] == 0.0

def test_impossible_age_becomes_nan_and_missing_handled():
    d = add_features(_row(age=140, distance_km=np.nan, booking_channel=None))
    assert np.isnan(d["age"].iloc[0])
    assert d["booking_channel"].iloc[0] == "unknown"
    out = build_preprocessor().fit(pd.concat([add_features(_row())] * 3)).transform(d)
    assert not np.isnan(out).any()

def test_unknown_category_does_not_crash():
    prep = build_preprocessor().fit(add_features(_row()))
    prep.transform(add_features(_row(department="Brand New Dept")))

def test_no_forbidden_or_sensitive_columns_in_features():
    assert not set(NUMERIC + CATEGORICAL) & set(FORBIDDEN)
    with pytest.raises(ValueError):
        assert_no_forbidden(["age", "diagnosis"])
    assert "gender" not in NUMERIC + CATEGORICAL   # sensitive attr used for audit only

