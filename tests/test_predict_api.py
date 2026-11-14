import pytest
from fastapi.testclient import TestClient
from src.config import MODEL_PATH

pytestmark = pytest.mark.skipif(not MODEL_PATH.exists(), reason="run `python -m src.train` first")

from api.app import app  # noqa: E402

client = TestClient(app)

GOOD = {"age": 27, "distance_km": 18.5, "lead_time_days": 34, "appt_weekday": "Monday", "appt_hour": 8,
        "department": "Dental", "booking_channel": "phone", "reminder_scheduled": "no",
        "is_follow_up": "no", "prev_visits": 4, "prev_no_shows": 2}

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_predict_returns_valid_probability_and_disclaimer():
    r = client.post("/predict", json=GOOD).json()
    assert 0.0 <= r["no_show_probability"] <= 1.0
    assert r["risk_band"] in {"low", "medium", "high"}
    assert "Staff" in r["disclaimer"] or "staff" in r["disclaimer"]
    assert len(r["top_factors"]) > 0

def test_prediction_is_deterministic_and_model_driven():
    a = client.post("/predict", json=GOOD).json()["no_show_probability"]
    b = client.post("/predict", json=GOOD).json()["no_show_probability"]
    assert a == b
    safe = {**GOOD, "lead_time_days": 1, "reminder_scheduled": "yes", "prev_no_shows": 0,
            "booking_channel": "online", "appt_hour": 11, "appt_weekday": "Wednesday"}
    assert client.post("/predict", json=safe).json()["no_show_probability"] < a  # risky > safe

def test_bad_input_rejected():
    assert client.post("/predict", json={**GOOD, "appt_weekday": "Sunday"}).status_code == 422
    assert client.post("/predict", json={**GOOD, "prev_no_shows": 9}).status_code == 422
    assert client.post("/predict", json={**GOOD, "age": -3}).status_code == 422

def test_batch_ranked_by_risk():
    safe = {**GOOD, "lead_time_days": 1, "reminder_scheduled": "yes", "prev_no_shows": 0}
    res = client.post("/predict_batch", json=[safe, GOOD]).json()["ranked_by_risk"]
    assert res[0]["no_show_probability"] >= res[1]["no_show_probability"]

