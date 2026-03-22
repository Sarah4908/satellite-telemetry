from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
import requests
import os
from collections import deque
from threading import Lock
from rag.rag_engine import generate_explanation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained pipeline
pipeline = joblib.load("anomaly_pipeline.pkl")
model = pipeline["model"]
scaler = pipeline["scaler"]
features = pipeline["features"]

# Validate feature order matches what was used at training time
EXPECTED_FEATURES = [
    "temperature", "voltage", "altitude",
    "temp_delta", "volt_delta", "rolling_temp_mean"
]
if features != EXPECTED_FEATURES:
    raise RuntimeError(
        f"Pipeline feature mismatch. Expected {EXPECTED_FEATURES}, got {features}. "
        "Re-run train_model.py to regenerate anomaly_pipeline.pkl."
    )

SPRING_URL = os.getenv("SPRING_URL", "http://localhost:8080")


# Satellite state — holds previous readings for delta and rolling mean computation
class SatelliteState:
    def __init__(self):
        self.previous_temp = None
        self.previous_voltage = None
        self.temp_history = deque(maxlen=10)


satellite_states = {}
state_lock = Lock()


@app.on_event("startup")
def load_state_from_db():
    """
    On startup, load the last known readings per satellite from PostgreSQL
    via Spring Boot's API. This seeds the in-memory state so that delta
    features and rolling mean are accurate immediately after a restart.
    Without this, the first reading after a restart would have temp_delta=0
    and volt_delta=0 which could cause incorrect anomaly scores.
    """
    try:
        res = requests.get(f"{SPRING_URL}/api/telemetry", timeout=5)
        res.raise_for_status()
        records = res.json()

        if not records:
            print("[INFO] No existing telemetry in DB. Starting with empty state.")
            return

        # Sort all records by timestamp ascending so we process oldest first
        records_sorted = sorted(
            [r for r in records if r.get("satelliteId") and r.get("temperature") is not None],
            key=lambda r: r.get("timestamp", "")
        )

        for record in records_sorted:
            sid = record["satelliteId"]
            with state_lock:
                if sid not in satellite_states:
                    satellite_states[sid] = SatelliteState()
                state = satellite_states[sid]
                state.previous_temp = record["temperature"]
                state.previous_voltage = record["voltage"]
                state.temp_history.append(record["temperature"])

        print(f"[INFO] Seeded in-memory state for {len(satellite_states)} satellite(s) from DB.")

    except requests.exceptions.ConnectionError:
        print("[WARN] Could not reach Spring Boot on startup — starting with empty state.")
    except requests.exceptions.Timeout:
        print("[WARN] Spring Boot startup seed timed out — starting with empty state.")
    except Exception as e:
        print(f"[WARN] Could not load state from DB: {e} — starting with empty state.")


# Input schema
class TelemetryInput(BaseModel):
    satelliteId: str
    temperature: float
    voltage: float
    altitude: float


@app.post("/predict")
def predict(data: TelemetryInput):
    with state_lock:
        if data.satelliteId not in satellite_states:
            satellite_states[data.satelliteId] = SatelliteState()
        state = satellite_states[data.satelliteId]

        # Delta features
        if state.previous_temp is None:
            temp_delta = 0.0
            volt_delta = 0.0
        else:
            temp_delta = data.temperature - state.previous_temp
            volt_delta = data.voltage - state.previous_voltage

        state.previous_temp = data.temperature
        state.previous_voltage = data.voltage

        # Rolling mean
        state.temp_history.append(data.temperature)
        rolling_temp_mean = float(np.mean(state.temp_history))

    # Prepare features in the same order as training
    input_array = np.array([[
        data.temperature,
        data.voltage,
        data.altitude,
        temp_delta,
        volt_delta,
        rolling_temp_mean
    ]])

    input_scaled = scaler.transform(input_array)
    prediction = model.predict(input_scaled)[0]
    score = float(model.decision_function(input_scaled)[0])
    is_anomaly = bool(prediction == -1)

    result = {
        "satelliteId": data.satelliteId,
        "temperature": data.temperature,
        "voltage": data.voltage,
        "altitude": data.altitude,
        "temp_delta": float(temp_delta),
        "volt_delta": float(volt_delta),
        "rolling_temp_mean": rolling_temp_mean,
        "anomalyScore": score,
        "isAnomaly": is_anomaly,
    }

    # Generate explanation for anomalies via RAG
    if is_anomaly:
        try:
            result["explanation"] = generate_explanation(result)
        except Exception as e:
            print(f"[WARN] RAG explanation failed: {e}")
            result["explanation"] = "Explanation service temporarily unavailable."
    else:
        result["explanation"] = "No anomaly detected."

    return result


@app.get("/health")
def health():
    return {"status": "ML microservice running"}