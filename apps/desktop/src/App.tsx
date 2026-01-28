import { useState, useEffect, useRef } from 'react'
import './App.css'

interface LogEntry {
  timestamp: string;
  level: string;
  component: string;
  message: string;
}

const API_URL = "http://127.0.0.1:12345";

function App() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState<"disconnected" | "connected">("disconnected");
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const logEndRef = useRef<HTMLDivElement>(null);

  // Poll for logs and status
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch(`${API_URL}/logs`);
        if (res.ok) {
          const data = await res.json();
          setLogs(data);
          setStatus("connected");
        } else {
          setStatus("disconnected");
        }
      } catch (e) {
        setStatus("disconnected");
      }
    };

    const interval = setInterval(fetchLogs, 1000);
    return () => clearInterval(interval);
  }, []);

  // Fetch config on mount
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await fetch(`${API_URL}/config`);
        if (res.ok) {
          const data = await res.json();
          if (data.GOOGLE_API_KEY) {
            setApiKey(data.GOOGLE_API_KEY);
          }
        }
      } catch (e) {
        console.error("Failed to fetch config", e);
      }
    };
    fetchConfig();
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const runTask = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/run-task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_name: "daily-brief" }),
      });
    } catch (e) {
      console.error("Failed to run task", e);
    } finally {
      setTimeout(() => setLoading(false), 1000);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Contex MVP</h1>
        <div className={`status-badge ${status}`}>
          <div className="dot"></div>
          {status === "connected" ? "Sidecar Connected" : "Sidecar Disconnected"}
        </div>
      </header>

      <main className="main-content">
        <div className="card task-card">
          <h2>Daily Brief Agent</h2>
          <p>Generates a daily news summary using local Python + Docker.</p>
          <button onClick={runTask} disabled={loading || status === "disconnected"}>
            {loading ? "Starting..." : "Run Task"}
          </button>
        </div>

        <div className="log-console">
          <div className="log-header">
            <h3>System Logs</h3>
            <span className="log-count">{logs.length} lines</span>
          </div>
          <div className="log-body">
            {logs.length === 0 && <div className="log-empty">Waiting for logs...</div>}
            {logs.map((log, i) => (
              <div key={i} className={`log-line ${log.level.toLowerCase()}`}>
                <span className="timestamp">{log.timestamp.split('T')[1].slice(0,8)}</span>
                <span className="component">[{log.component}]</span>
                <span className="message">{log.message}</span>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
