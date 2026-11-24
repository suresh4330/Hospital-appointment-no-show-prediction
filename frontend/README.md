# CareAttend AI — Hospital Appointment No-Show Prediction Frontend

* **Live Web App:** https://hospital-appointment-no-show-predic-nine.vercel.app
* **Live API Backend:** https://hospital-appointment-no-show-prediction-v3hj.onrender.com

A modern, responsive, accessible React 18 web interface for clinical decision-support triage, built with **Vite**, **Tailwind CSS**, and **Lucide React**.

---

## Features

1. **Single Appointment Triage Calculator (`/`)**:
   - Immediate no-show probability estimation at the point of booking.
   - Interactive inputs with client-side and server-side validation (e.g. `past no-shows <= past visits`).
   - One-click clinical presets (*High-Risk Dental*, *Low-Risk GP*, *Senior Physiotherapy*, *Pediatric First Visit*).
   - Radial Risk Gauge with dynamic color transitions (Low: Emerald, Medium: Amber, High: Rose).
   - Explainable AI breakdown cards (counterfactual occlusion factors showing which patient inputs raised or lowered risk).
   - Copyable triage summary and prominent clinical decision-support disclaimer.

2. **Daily Batch Schedule Triage Queue (`/batch`)**:
   - Batch risk prediction and automated ranking from highest to lowest risk via `POST /predict_batch`.
   - Real-time search and multi-criteria filters by Clinic Department and Risk Band.
   - Clinical Outreach Checklist (toggle *Call Completed*, *SMS Dispatched*).
   - Instant CSV export for staff call sheets.

3. **Model Intelligence & Fairness Audit (`/analytics`)**:
   - Real-time backend connectivity check via `GET /health`.
   - Verified test metrics (Recall: 81.1%, Precision: 30.9%, F1: 0.448, PR-AUC: 0.466, Brier score: 0.128).
   - Confusion matrix breakdown (846 TN, 615 FP, 64 FN, 275 TP).
   - Cost optimization analysis demonstrating 17.8% cost savings over heuristic clinic rules.
   - Protected demographic subgroup fairness audit table (Age group and Gender parity).

4. **Staff Authentication & Dark Mode**:
   - Role switcher / staff sign-in (*Clinical Receptionist*, *Triage Coordinator*, *Operations Lead*) with persistent session storage.
   - Full dark mode support with system preference auto-detection and persistence.

---

## Tech Stack

* **Framework:** React 18
* **Build Tool:** Vite 5
* **Routing:** React Router v6
* **Styling:** Tailwind CSS v3
* **Forms:** React Hook Form
* **HTTP Client:** Axios
* **Icons:** Lucide React

---

## Quick Start

### 1. Start the FastAPI Backend
From the project root:
```bash
# Activate python virtual environment
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Linux / macOS

# Start inference API
uvicorn api.app:app --port 8000 --reload
```
API Documentation will be live at `http://127.0.0.1:8000/docs`.

### 2. Start the React Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Environment Configuration

Configuration is located in `frontend/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```
*(In development, Vite also proxies `/api` directly to `http://127.0.0.1:8000`)*.

---

## Production Build

```bash
cd frontend
npm run build
npm run preview
```
Production assets are generated in `frontend/dist/`.
