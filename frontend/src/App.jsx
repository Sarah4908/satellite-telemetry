import { useState } from "react";
import "./App.css";

function App() {
  const [form, setForm] = useState({
    satelliteId: "",
    temperature: "",
    voltage: "",
    altitude: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // use relative paths; container nginx will proxy to appropriate services
  const ML_URL = "";          // empty prefix => same origin
  const BACKEND_URL = "";

  const submitTelemetry = async () => {
    setLoading(true);
    setResult(null);

    try {
      // call ML microservice for prediction
      const response = await fetch(`/predict`, {
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          satelliteId: form.satelliteId,
          temperature: parseFloat(form.temperature),
          voltage: parseFloat(form.voltage),
          altitude: parseFloat(form.altitude),
        }),
      });

      const data = await response.json();
      setResult(data);

      // send the result to the backend so it can be stored and explained
      const saveResp = await fetch(`/api/ml/result`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const saved = await saveResp.json();
      // backend might add explanation/timestamp
      setResult(saved);

      // refresh history after saving
      fetchHistory();
    } catch (err) {
      alert("One of the backends is not reachable");
    }

    setLoading(false);
  };

  // history of stored telemetry
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`/api/telemetry`);
      const arr = await res.json();
      setHistory(arr);
    } catch (e) {
      // ignore
    }
  };

  // load history on mount
  useState(() => {
    fetchHistory();
  }, []);

  return (
    <div className="container">
      <h1>🚀 Satellite Telemetry Dashboard</h1>

      <div className="card">
        <input name="satelliteId" placeholder="Satellite ID" onChange={handleChange} />
        <input name="temperature" placeholder="Temperature" onChange={handleChange} />
        <input name="voltage" placeholder="Voltage" onChange={handleChange} />
        <input name="altitude" placeholder="Altitude" onChange={handleChange} />

        <button onClick={submitTelemetry}>
          {loading ? "Processing..." : "Send Telemetry"}
        </button>
      </div>

      {result && (
        <div className="result">
          <h2>🔍 Analysis Result</h2>
          <p><b>Anomaly Score:</b> {result.anomalyScore}</p>
          <p><b>Status:</b> {result.isAnomaly ? "⚠️ Anomaly Detected" : "✅ Normal"}</p>
          <p><b>Temp Delta:</b> {result.temp_delta}</p>
          <p><b>Volt Delta:</b> {result.volt_delta}</p>
          <p><b>Rolling Mean:</b> {result.rolling_temp_mean}</p>
          {result.explanation && (
            <p><b>Explanation:</b> {result.explanation}</p>
          )}
        </div>
      )}

      {/* history table */}
      {history.length > 0 && (
        <div className="history">
          <h2>📜 Stored Telemetry</h2>
          <table>
            <thead>
              <tr>
                <th>Satellite</th>
                <th>Temp</th>
                <th>Volt</th>
                <th>Alt</th>
                <th>Anomaly?</th>
                <th>Explanation</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {history.map((r, i) => (
                <tr key={i}>
                  <td>{r.satelliteId}</td>
                  <td>{r.temperature}</td>
                  <td>{r.voltage}</td>
                  <td>{r.altitude}</td>
                  <td>{r.anomaly ? "⚠️" : ""}</td>
                  <td>{r.explanation || ""}</td>
                  <td>{new Date(r.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {result.isAnomaly && result.explanation && (
            <p><b>Explanation:</b> {result.explanation}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;