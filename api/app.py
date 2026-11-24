"""FastAPI inference service.  Run:  uvicorn api.app:app --reload
Docs UI: http://127.0.0.1:8000/docs"""
import sys
from pathlib import Path

# Ensure project root is in sys.path so 'src' can be resolved
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import List, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.config import META_PATH
from src.predict import load_artifact, predict_one, predict_records

app = FastAPI(title="Hospital Appointment No-Show Predictor",
              description="Decision-support only. Predicts probability of a missed appointment. "
                          "Never used for diagnosis/urgency; staff review every flagged case.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Weekday = Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

class Appointment(BaseModel):
    age: int = Field(..., ge=0, le=110)
    distance_km: Optional[float] = Field(None, ge=0, le=500)
    lead_time_days: int = Field(..., ge=0, le=365, description="Days between booking and appointment")
    appt_weekday: Weekday
    appt_hour: int = Field(..., ge=7, le=18)
    department: Literal["General Practice", "Pediatrics", "Dental", "Eye Clinic", "Physiotherapy"]
    booking_channel: Literal["phone", "online", "front_desk"]
    reminder_scheduled: Literal["yes", "no"]
    is_follow_up: Literal["yes", "no"]
    prev_visits: int = Field(0, ge=0)
    prev_no_shows: int = Field(0, ge=0)
    model_config = {"json_schema_extra": {"example": {
        "age": 27, "distance_km": 18.5, "lead_time_days": 34, "appt_weekday": "Monday", "appt_hour": 8,
        "department": "Dental", "booking_channel": "phone", "reminder_scheduled": "no",
        "is_follow_up": "no", "prev_visits": 4, "prev_no_shows": 2}}}

@app.get("/health")
def health():
    art = load_artifact()
    return {"status": "ok", "threshold": art["threshold"], "features": art["features"]}

@app.post("/predict")
def predict(a: Appointment):
    if a.prev_no_shows > a.prev_visits:
        raise HTTPException(422, "prev_no_shows cannot exceed prev_visits")
    return predict_one(a.model_dump())

@app.post("/predict_batch")
def predict_batch(items: List[Appointment]):
    if len(items) > 500:
        raise HTTPException(413, "Max 500 appointments per request")
    res = predict_records([i.model_dump() for i in items], with_explanation=False)
    order = sorted(range(len(res)), key=lambda i: -res[i]["no_show_probability"])
    return {"ranked_by_risk": [{"index": i, **res[i]} for i in order]}

@app.get("/meta")
def get_metadata():
    import json
    if META_PATH.exists():
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Serve pre-built React frontend if available (unified deployment)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

dist_dir = PROJECT_ROOT / "frontend" / "dist"
if dist_dir.exists():
    assets_dir = dist_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = dist_dir / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")



