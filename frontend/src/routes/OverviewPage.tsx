import { BookOpen, Check, Copy, History, Plus, RefreshCw, Terminal, WifiOff } from "lucide-react";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";

import { listCampaigns } from "../api/campaigns";
import { getHealth } from "../api/health";
import { apiBaseUrl } from "../config";
import type { Campaign } from "../types/campaigns";
import type { HealthResponse } from "../types/health";

type HealthRequestState =
  | { status: "loading" }
  | { status: "success"; health: HealthResponse }
  | { status: "error"; message: string };

type CampaignShortcutState = { status: "loading" } | { status: "ready"; campaigns: Campaign[] } | { status: "error" };

export function OverviewPage() {
  const [requestState, setRequestState] = useState<HealthRequestState>({ status: "loading" });
  const [campaignShortcutState, setCampaignShortcutState] = useState<CampaignShortcutState>({
    status: "loading",
  });
  const [isReconnectSpinning, setIsReconnectSpinning] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const [quickDraft, setQuickDraft] = useState(() => window.localStorage.getItem("gm-workspace:quick-draft") ?? "");

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

  useEffect(() => {
    const abortController = new AbortController();

    async function loadCampaignShortcuts() {
      try {
        const campaigns = await listCampaigns({ signal: abortController.signal });
        setCampaignShortcutState({ campaigns: campaigns.slice(0, 3), status: "ready" });
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setCampaignShortcutState({ status: "error" });
      }
    }

    void loadCampaignShortcuts();

    return () => {
      abortController.abort();
    };
  }, []);

  useEffect(() => {
    window.localStorage.setItem("gm-workspace:quick-draft", quickDraft);
  }, [quickDraft]);

  function handleCopyCommand() {
    void navigator.clipboard.writeText("uv run uvicorn app.main:app --reload");
    setIsCopied(true);
    window.setTimeout(() => {
      setIsCopied(false);
    }, 1200);
  }

  function handleReconnect() {
    setIsReconnectSpinning(true);
    window.setTimeout(() => {
      setIsReconnectSpinning(false);
    }, 900);
  }

  return (
    <div className="page-stack">
      <section className="overview-context-header panel">
        <div className="page-header-copy">
          <h2 className="font-ui">Overview</h2>
        </div>
        <div className="page-header-actions">
          <div className="action-row">
            <Link className="primary-button" to="/entities/new">
              <Plus aria-hidden="true" size={15} strokeWidth={2.2} />
              New Entity
            </Link>
            <Link className="secondary-button overview-secondary-action" to="/campaigns/new">
              <Plus aria-hidden="true" size={15} strokeWidth={2.2} />
              New Campaign
            </Link>
          </div>
        </div>
      </section>
      <section className="utility-bar panel">
        {requestState.status === "success" ? (
          <>
            <div className="utility-bar-copy">
              <strong>Connection</strong>
              <span>API target: {apiBaseUrl}</span>
            </div>
            <div className="utility-bar-status">
              <span className="status-pill status-ok">Connected</span>
              <span>Backend status: {requestState.health.status}</span>
            </div>
          </>
        ) : null}
        {requestState.status === "loading" ? (
          <>
            <div className="utility-bar-copy">
              <strong>Connection</strong>
              <span>API target: {apiBaseUrl}</span>
            </div>
            <div className="utility-bar-status">
              <span className="status-pill">Checking</span>
            </div>
          </>
        ) : null}
        {requestState.status === "error" ? (
          <>
            <div className="utility-bar-copy">
              <WifiOff aria-hidden="true" size={14} strokeWidth={2.2} />
              <strong>Offline Mode: Backend Disconnected</strong>
            </div>
            <div className="utility-bar-status">
              <span className="status-pill status-error">Offline</span>
              <button className="utility-reconnect" type="button" onClick={handleReconnect}>
                <RefreshCw
                  aria-hidden="true"
                  className={isReconnectSpinning ? "spin-icon" : undefined}
                  size={13}
                  strokeWidth={2.2}
                />
                {isReconnectSpinning ? "Reconnecting..." : "Reconnect"}
              </button>
              <span className="status-error-copy">{requestState.message}</span>
            </div>
          </>
        ) : null}
      </section>
      <section className="overview-grid">
        <section className="panel overview-card">
          <div className="section-heading">
            <h3>
              <BookOpen aria-hidden="true" size={16} strokeWidth={2.1} />
              Session Scratchpad
            </h3>
            <p className="section-copy">Type quick notes here... they save locally.</p>
          </div>
          <label className="sr-only" htmlFor="quick-draft">
            Quick Draft
          </label>
          <textarea
            id="quick-draft"
            className="scratchpad"
            placeholder="Type quick notes here... they save locally."
            value={quickDraft}
            onChange={(event) => {
              setQuickDraft(event.target.value);
            }}
          />
        </section>
        <section className="panel overview-card">
          <div className="section-heading">
            <h3>
              <History aria-hidden="true" size={16} strokeWidth={2.1} />
              Recent Entities
            </h3>
          </div>
          <div className="recent-records">
            <article className="recent-record">
              <h4>Last Viewed Entity</h4>
              <p>No recent entity yet in this browser.</p>
            </article>
            <article className="recent-record">
              <h4>Campaign Shortcut</h4>
              {campaignShortcutState.status === "loading" ? <p>Loading campaign shortcuts...</p> : null}
              {campaignShortcutState.status === "error" ? <p>Campaign shortcuts unavailable.</p> : null}
              {campaignShortcutState.status === "ready" && campaignShortcutState.campaigns.length === 0 ? (
                <p>No campaigns yet.</p>
              ) : null}
              {campaignShortcutState.status === "ready" && campaignShortcutState.campaigns.length > 0 ? (
                <div className="campaign-shortcut-list">
                  {campaignShortcutState.campaigns.map((campaign) => (
                    <Link key={campaign.id} className="record-link" to={`/campaigns/${campaign.id}`}>
                      {campaign.name}
                    </Link>
                  ))}
                </div>
              ) : null}
            </article>
          </div>
        </section>
      </section>
      {requestState.status === "error" ? (
        <section className="panel command-callout">
          <div className="command-callout-copy">
            <strong>
              <Terminal aria-hidden="true" size={16} strokeWidth={2.1} />
              To enable AI extraction and sync, run the server:
            </strong>
            <code>uv run uvicorn app.main:app --reload</code>
          </div>
          <button className="secondary-button" type="button" onClick={handleCopyCommand}>
            {isCopied ? (
              <Check aria-hidden="true" size={15} strokeWidth={2.2} />
            ) : (
              <Copy aria-hidden="true" size={15} strokeWidth={2.2} />
            )}
            {isCopied ? "Copied" : "Copy"}
          </button>
        </section>
      ) : null}
    </div>
  );
}
