"""Central configuration: paths, seed, cost assumptions, feature lists."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "appointments.csv"
MODEL_PATH = ROOT / "models" / "model.joblib"
META_PATH = ROOT / "models" / "model_meta.json"
REPORTS = ROOT / "reports"
SEED = 42
TARGET = "no_show"

# Business cost assumptions (state and justify these in your report).
# A missed no-show wastes a clinic slot; a false alarm costs one reminder call/SMS.
COST_FN = 10.0   # no-show we failed to flag  (lost slot value, arbitrary units)
COST_FP = 2.0    # attender we flagged        (extra reminder effort)

# Columns known AT BOOKING TIME (allowed as inputs)
NUMERIC = [
    "age", "distance_km", "lead_time_days", "appt_hour",
    "prev_visits", "prev_no_shows", "prev_no_show_rate", "prev_attended",
]
CATEGORICAL = [
    "appt_weekday", "department", "booking_channel",
    "reminder_scheduled", "is_follow_up", "hour_bucket", "lead_bucket", "is_first_visit",
]

# Columns that must NEVER be used as inputs (future info / sensitive / target)
FORBIDDEN = [
    "no_show", "appointment_status", "check_in_time", "wait_minutes",
    "diagnosis", "treatment", "urgency", "outcome",
]

# Used only for fairness auditing, NOT as model inputs
AUDIT_COLS = ["gender", "age_group"]
