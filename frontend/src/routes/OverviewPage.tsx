import { useEffect, useState } from "react";

import { getHealth } from "../api/health";
import { apiBaseUrl } from "../config";
import type { HealthResponse } from "../types/health";

type HealthRequestState =
  | { status: "loading" }
  | { status: "success"; health: HealthResponse }
  | { status: "error"; message: string };

export function OverviewPage() {
  const [requestState, setRequestState] = useState<HealthRequestState>({ status: "loading" });

  useEffect(() => {
    const abortController = new AbortController();

    async function loadHealth() {
      try {
        const nextHealth = await getHealth({ signal: abortController.signal });
        setRequestState({ status: "success", health: nextHealth });
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setRequestState({
          status: "error",
          message: error instanceof Error ? error.message : "Unknown connection error.",
        });
      }
    }

    void loadHealth();

    return () => {
      abortController.abort();
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
          {requestState.status === "success" ? (
            <span className="status-pill status-ok">Connected</span>
          ) : null}
          {requestState.status === "error" ? (
            <span className="status-pill status-error">Unreachable</span>
          ) : null}
          {requestState.status === "loading" ? <span className="status-pill">Checking</span> : null}
        </div>
        <p className="status-line">API target: {apiBaseUrl}</p>
        {requestState.status === "success" ? (
          <p className="status-line">Backend status: {requestState.health.status}</p>
        ) : null}
        {requestState.status === "error" ? (
          <p className="status-line">
            Start the backend with `uv run uvicorn app.main:app --reload` and confirm the API base
            URL matches `frontend/.env`.
          </p>
        ) : null}
        {requestState.status === "error" ? (
          <p className="status-error-copy">{requestState.message}</p>
        ) : null}
      </section>
    </section>
  );
}
