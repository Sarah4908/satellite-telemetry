import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

  const [form, setForm] = useState({
    satelliteId: "",
    temperature: "",
    voltage: "",
    altitude: "",
  });

  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/telemetry`);
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("History fetch failed");
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const submitTelemetry = async () => {
    if (!form.satelliteId) {
      setError("Please enter a Satellite ID.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${BACKEND_URL}/api/telemetry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          satelliteId: form.satelliteId,
          temperature: parseFloat(form.temperature),
          voltage: parseFloat(form.voltage),
          altitude: parseFloat(form.altitude),
        }),
      });

      if (!res.ok) throw new Error("Backend request failed");

      const saved = await res.json();
      setResult(saved);
      fetchHistory();
    } catch (err) {
      setError("Backend is not reachable. Make sure all services are running.");
    }

    setLoading(false);
  };

  return (
    <div className="dashboard">
      <h1>Satellite Telemetry Dashboard</h1>

      {error && <div className="error">{error}</div>}

      <div className="grid">
        {/* INPUT PANEL */}
        <div className="card">
          <h2>Send Telemetry</h2>
          <input name="satelliteId" placeholder="Satellite ID" onChange={handleChange} />
          <input name="temperature" placeholder="Temperature" onChange={handleChange} />
          <input name="voltage" placeholder="Voltage" onChange={handleChange} />
          <input name="altitude" placeholder="Altitude" onChange={handleChange} />
          <button onClick={submitTelemetry}>
            {loading ? "Processing..." : "Send"}
          </button>
        </div>

        {/* RESULT PANEL */}
        <div className="card">
          <h2>ML Analysis</h2>
          {result ? (
            <>
              <div className={`status ${result.anomaly ? "anomaly" : "normal"}`}>
                {result.anomaly ? "Anomaly Detected" : "Normal"}
              </div>
              <p><b>Anomaly Score:</b> {result.anomalyScore}</p>
              <p><b>Temperature:</b> {result.temperature}</p>
              <p><b>Voltage:</b> {result.voltage}</p>
              <p><b>Altitude:</b> {result.altitude}</p>
              {result.explanation && (
                <div className="explanation">
                  <b>Explanation:</b>
                  <p>{result.explanation}</p>
                </div>
              )}
            </>
          ) : (
            <p>No data yet.</p>
          )}
        </div>
      </div>

      {/* HISTORY TABLE */}
      <div className="card history">
        <h2>Telemetry History</h2>
        {history.length === 0 ? (
          <p>No telemetry stored yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Satellite</th>
                <th>Temp</th>
                <th>Volt</th>
                <th>Alt</th>
                <th>Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item, i) => (
                <tr key={i}>
                  <td>{item.satelliteId}</td>
                  <td>{item.temperature}</td>
                  <td>{item.voltage}</td>
                  <td>{item.altitude}</td>
                  <td>{item.anomaly ? "Anomaly" : "Normal"}</td>
                  <td>{item.timestamp ? new Date(item.timestamp).toLocaleString() : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default App;