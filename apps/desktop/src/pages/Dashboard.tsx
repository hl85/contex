import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom';

interface LogEntry {
  timestamp: string;
  level: string;
  component: string;
  message: string;
}

const API_URL = "http://127.0.0.1:12345";

export default function Dashboard() {
  const navigate = useNavigate();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState<"disconnected" | "connected">("disconnected");
  const [loading, setLoading] = useState(false);
  const [missingKey, setMissingKey] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Check for API Key on mount
  useEffect(() => {
    fetch(`${API_URL}/config`)
      .then(res => res.json())
      .then(data => {
        if (!data.GOOGLE_API_KEY || data.GOOGLE_API_KEY === "your_api_key_here") {
          setMissingKey(true);
        }
      })
      .catch(() => {});
  }, []);

  const logContainerRef = useRef<HTMLDivElement>(null);
  const isUserAtBottomRef = useRef(true);

  // Handle scroll events to detect if user is at bottom
  const handleScroll = () => {
    if (logContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
      // If within 50px of bottom, consider it "at bottom"
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      isUserAtBottomRef.current = isAtBottom;
    }
  };

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

  // Auto-scroll logs
  useEffect(() => {
    if (isUserAtBottomRef.current) {
      logEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
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

  const clearLogs = async () => {
    try {
      setLogs([]); // Optimistic update
      await fetch(`${API_URL}/logs`, { method: "DELETE" });
    } catch (e) {
      console.error("Failed to clear logs", e);
    }
  };

  return (
    <div className="container">
      <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h1>Contex MVP</h1>
          <div className={`status-badge ${status}`}>
            <div className="dot"></div>
            {status === "connected" ? "Sidecar Connected" : "Sidecar Disconnected"}
          </div>
        </div>
        <button onClick={() => navigate("/settings")} className="secondary-btn" style={{ padding: '8px 16px', background: '#334155', border: 'none', borderRadius: '4px', color: 'white', cursor: 'pointer' }}>
          Settings
        </button>
      </header>

      <main className="main-content">
        {missingKey && (
          <div style={{ background: '#7f1d1d', color: '#fca5a5', padding: '10px', borderRadius: '4px', marginBottom: '20px' }}>
            <strong>⚠️ Configuration Missing:</strong> Please go to Settings and configure your Google API Key (or set it in config.json).
          </div>
        )}
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span className="log-count">{logs.length} lines</span>
              <button 
                className="action-btn"
                onClick={clearLogs} 
                title="Clear logs"
                style={{ fontSize: '0.75rem', padding: '4px 8px', border: '1px solid #334155' }}
              >
                Clear
              </button>
            </div>
          </div>
          <div className="log-body" ref={logContainerRef} onScroll={handleScroll}>
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
