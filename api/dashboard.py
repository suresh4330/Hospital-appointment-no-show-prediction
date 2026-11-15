"""Optional staff dashboard.  Run:  streamlit run api/dashboard.py"""
import sys
from pathlib import Path

# Ensure project root is in sys.path so 'src' can be resolved
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st
from src.predict import predict_one

st.set_page_config(page_title="No-Show Risk (decision support)")
st.title("Appointment no-show risk")
st.warning("Decision-support only. Not a clinical tool. A staff member must review before any action.")

c1, c2 = st.columns(2)
rec = {
    "age": c1.number_input("Age", 0, 110, 30),
    "distance_km": c1.number_input("Distance (km)", 0.0, 500.0, 8.0),
    "lead_time_days": c1.number_input("Lead time (days)", 0, 365, 14),
    "appt_weekday": c1.selectbox("Weekday", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
    "appt_hour": c1.slider("Hour", 8, 16, 10),
    "department": c2.selectbox("Department", ["General Practice", "Pediatrics", "Dental",
                                              "Eye Clinic", "Physiotherapy"]),
    "booking_channel": c2.selectbox("Booking channel", ["phone", "online", "front_desk"]),
    "reminder_scheduled": c2.selectbox("Reminder scheduled?", ["yes", "no"]),
    "is_follow_up": c2.selectbox("Follow-up visit?", ["yes", "no"]),
    "prev_visits": c2.number_input("Previous visits", 0, 100, 0),
    "prev_no_shows": c2.number_input("Previous no-shows", 0, 100, 0),
}

if st.button("Predict"):
    if rec["prev_no_shows"] > rec["prev_visits"]:
        st.error("Previous no-shows cannot exceed previous visits.")
    else:
        r = predict_one(rec)
        st.metric("No-show probability", f"{r['no_show_probability']:.1%}", r["risk_band"].upper())
        st.info(r["suggested_action"])
        st.subheader("Top factors for this prediction")
        st.dataframe(pd.DataFrame(r["top_factors"]))
        st.caption("Probabilities are estimates from synthetic training data; "
                   "see limitations in the report.")

