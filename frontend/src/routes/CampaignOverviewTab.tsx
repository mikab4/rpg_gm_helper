import { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";

import { SectionPanel } from "../components/SectionPanel";
import type { CampaignWorkspaceContext } from "./CampaignWorkspacePage";

export function CampaignOverviewTab() {
  const { campaign } = useOutletContext<CampaignWorkspaceContext>();
  const quickNotesStorageKey = `gm-workspace:campaign-quick-notes:${campaign.id}`;
  const [quickNotes, setQuickNotes] = useState("");
  const pendingHydrationKey = useRef<string | null>(null);

  useEffect(() => {
    pendingHydrationKey.current = quickNotesStorageKey;
    setQuickNotes(window.localStorage.getItem(quickNotesStorageKey) ?? "");
  }, [quickNotesStorageKey]);

  useEffect(() => {
    if (pendingHydrationKey.current === quickNotesStorageKey) {
      pendingHydrationKey.current = null;
      return;
    }

    window.localStorage.setItem(quickNotesStorageKey, quickNotes);
  }, [quickNotes, quickNotesStorageKey]);

  return (
    <div className="campaign-overview-layout">
      <SectionPanel title="Campaign Summary">
        <p className="campaign-summary-text">{campaign.description ?? "No description yet."}</p>
      </SectionPanel>
      <div className="campaign-overview-grid">
        <SectionPanel title="Recent Activity">
          <p className="campaign-support-copy">Syncing with chronological log...</p>
        </SectionPanel>
        <SectionPanel title="Quick Notes">
          <label className="sr-only" htmlFor="campaign-quick-notes">
            Quick Notes
          </label>
          <textarea
            id="campaign-quick-notes"
            className="campaign-quick-notes"
            placeholder="Draft session ideas..."
            rows={5}
            value={quickNotes}
            onChange={(event) => {
              setQuickNotes(event.target.value);
            }}
          />
        </SectionPanel>
      </div>
    </div>
  );
}
