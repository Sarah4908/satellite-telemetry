from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib
import requests
from collections import deque
from threading import Lock
from rag.rag_engine import generate_explanation

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load trained pipeline
pipeline = joblib.load("anomaly_pipeline.pkl")
model = pipeline["model"]
scaler = pipeline["scaler"]
features = pipeline["features"]

SPRING_URL = "http://backend:8080/api/ml/result"


# Satellite State Manager
class SatelliteState:
    def __init__(self):
        self.previous_temp = None
        self.previous_voltage = None
        self.temp_history = deque(maxlen=10)

satellite_states = {}
state_lock = Lock()


# Input Schema
class TelemetryInput(BaseModel):
    satelliteId: str
    temperature: float
    voltage: float
    altitude: float


# Prediction Endpoint
@app.post("/predict")
def predict(data: TelemetryInput):

    with state_lock:
        if data.satelliteId not in satellite_states:
            satellite_states[data.satelliteId] = SatelliteState()

        state = satellite_states[data.satelliteId]

    # Delta Features
    if state.previous_temp is None:
        temp_delta = 0
        volt_delta = 0
    else:
        temp_delta = data.temperature - state.previous_temp
        volt_delta = data.voltage - state.previous_voltage

    state.previous_temp = data.temperature
    state.previous_voltage = data.voltage

    # Rolling Mean 
    state.temp_history.append(data.temperature)
    rolling_temp_mean = np.mean(state.temp_history)

    # Prepare Features
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
    score = model.decision_function(input_scaled)[0]

    result = {
        "satelliteId": data.satelliteId,
        "temperature": data.temperature,
        "voltage": data.voltage,
        "altitude": data.altitude,
        "temp_delta": float(temp_delta),
        "volt_delta": float(volt_delta),
        "rolling_temp_mean": float(rolling_temp_mean),
        "anomalyScore": float(score),
        "isAnomaly": bool(prediction == -1)
    }
    if prediction == -1:
        try:
            explanation = generate_explanation(result)
        except Exception as e:
            print("RAG failed:", e)
            explanation = "Explanation service temporarily unavailable."
    else:
        explanation = "No anomaly detected."

    result["explanation"] = explanation

    try:
        requests.post(SPRING_URL, json=result, timeout=2)
    except Exception as e:
        print("Failed to send to Spring:", e)
    return result
   

@app.get("/health")
def health():
    return {"status": "ML microservice running"}