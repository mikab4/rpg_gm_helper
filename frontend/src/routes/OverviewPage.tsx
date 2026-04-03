import { useEffect, useState } from "react";

import { getHealth } from "../api/health";
import { apiBaseUrl } from "../config";
import type { HealthResponse } from "../types/health";

export function OverviewPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    async function loadHealth() {
      try {
        const nextHealth = await getHealth();

        if (isActive) {
          setHealth(nextHealth);
          setErrorMessage(null);
        }
      } catch (error) {
        if (isActive) {
          setErrorMessage(error instanceof Error ? error.message : "Unknown connection error.");
        }
      }
    }

    void loadHealth();

    return () => {
      isActive = false;
    };
  }, []);

  return (
    <section className="panel overview-grid">
      <div className="hero">
        <p className="eyebrow">Frontend Scaffold</p>
        <h2>Run the app, click around, and confirm the backend is reachable.</h2>
        <p className="lede">
          The routed shell is in place. CRUD screens stay intentionally shallow until the backend
          contracts move beyond the current health endpoint.
        </p>
      </div>
      <section className="status-card">
        <div className="status-card-header">
          <h3>Connection</h3>
          {health ? <span className="status-pill status-ok">Connected</span> : null}
          {errorMessage ? <span className="status-pill status-error">Unreachable</span> : null}
          {!health && !errorMessage ? <span className="status-pill">Checking</span> : null}
        </div>
        <p className="status-line">API target: {apiBaseUrl}</p>
        {health ? <p className="status-line">Backend status: {health.status}</p> : null}
        {errorMessage ? (
          <p className="status-line">
            Start the backend with `uv run uvicorn app.main:app --reload` and confirm the API base
            URL matches `frontend/.env`.
          </p>
        ) : null}
        {errorMessage ? <p className="status-error-copy">{errorMessage}</p> : null}
      </section>
    </section>
  );
}
