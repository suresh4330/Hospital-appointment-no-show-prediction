# Leakage and Sensitive-Data Audit

**Prediction point:** the moment the appointment is booked. Allowed = known at that moment.

| Column | Known at booking? | Used as model input? | Reason |
| :--- | :---: | :---: | :--- |
| `age`, `distance_km` | yes | yes | static patient attributes |
| `lead_time_days` | yes | yes | `appointment_date - booking_date` is fixed at booking |
| `appt_weekday`, `appt_hour`, `department` | yes | yes | booking time choice (clinic type only) |
| `booking_channel`, `reminder_scheduled`, `is_follow_up` | yes | yes | recorded at booking |
| `prev_visits`, `prev_no_shows` | yes | yes | counted ONLY from appointments before this booking date |
| `prev_no_show_rate` | yes | yes | deterministic ratio (`prev_no_shows / prev_visits`) |
| `prev_attended` | yes | yes | deterministic difference (`prev_visits - prev_no_shows`) |
| `is_first_visit` | yes | yes | deterministic flag (`prev_visits == 0`) |
| `gender`, `age_group` | yes | no | sensitive; kept only for the fairness audit |
| `no_show` | no (outcome) | target only | target variable |
| `appointment_status`, `check_in_time` | no (future) | never | leaks outcome; blocked by guard |
| `wait_minutes` | no (future) | never | post-appointment feature |
| `diagnosis`, `treatment`, `urgency` | n/a | never | brief prohibits clinical variables |

**Enforced in code:** `src/features.assert_no_forbidden()` runs when the preprocessor is built and on every
inference request; `tests/test_features.py` asserts it. Split: chronological 70/15/15 by `appointment_date`;
test set touched once for the final report.
