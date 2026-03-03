import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib

np.random.seed(42)


# Generate Time-Series Telemetry
n_points = 6000

time = np.arange(n_points)

# Simulate realistic drift + noise
temperature = 72 + np.sin(time / 200) * 2 + np.random.normal(0, 1.5, n_points)
voltage = 3.3 - (time * 0.00002) + np.random.normal(0, 0.03, n_points)
altitude = 400 + np.sin(time / 300) * 3 + np.random.normal(0, 1, n_points)

df = pd.DataFrame({
    "temperature": temperature,
    "voltage": voltage,
    "altitude": altitude
})

# Inject Anomalies

anomaly_indices = np.random.choice(n_points, 200, replace=False)

df.loc[anomaly_indices, "temperature"] += np.random.uniform(20, 40, 200)
df.loc[anomaly_indices, "voltage"] -= np.random.uniform(0.5, 1.0, 200)

df["is_anomaly"] = 0
df.loc[anomaly_indices, "is_anomaly"] = 1

# Feature Engineering
df["temp_delta"] = df["temperature"].diff().fillna(0)
df["volt_delta"] = df["voltage"].diff().fillna(0)
df["rolling_temp_mean"] = df["temperature"].rolling(window=10).mean().bfill()
features = [
    "temperature",
    "voltage",
    "altitude",
    "temp_delta",
    "volt_delta",
    "rolling_temp_mean"
]

X = df[features]
y_true = df["is_anomaly"]


# Scale Features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# Train Model
model = IsolationForest(
    n_estimators=300,
    contamination=0.03,
    random_state=42
)

model.fit(X_scaled)

# Evaluate
y_pred = model.predict(X_scaled)
y_pred = np.where(y_pred == -1, 1, 0)

print("\nModel Evaluation:\n")
print(classification_report(y_true, y_pred))


# Train Final Model 
normal_data = df[df["is_anomaly"] == 0][features]
normal_scaled = scaler.fit_transform(normal_data)

final_model = IsolationForest(
    n_estimators=300,
    contamination=0.02,
    random_state=42
)

final_model.fit(normal_scaled)

joblib.dump({
    "model": final_model,
    "scaler": scaler,
    "features": features
}, "anomaly_pipeline.pkl")

print("\nTime-aware model saved successfully.")