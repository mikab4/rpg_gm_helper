import { Link, useOutletContext } from "react-router-dom";
import { useEffect, useState } from "react";

import { listCampaignEntities } from "../api/entities";
import { CampaignEntityRoster } from "../components/CampaignEntityRoster";
import { EntityQuickLookPanel } from "../components/EntityQuickLookPanel";
import { RequestStateBlock } from "../components/RequestStateBlock";
import { SectionPanel } from "../components/SectionPanel";
import type { Entity } from "../types/entities";
import type { CampaignWorkspaceContext } from "./CampaignWorkspacePage";

type CampaignEntitiesState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { entities: Entity[]; status: "ready" };

export function CampaignEntitiesTab() {
  const { campaign } = useOutletContext<CampaignWorkspaceContext>();
  const [pageState, setPageState] = useState<CampaignEntitiesState>({ status: "loading" });
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);

  useEffect(() => {
    const abortController = new AbortController();

    async function loadEntities() {
      try {
        const entities = await listCampaignEntities(campaign.id, undefined, abortController.signal);
        setPageState({ entities, status: "ready" });
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setPageState({
          message: error instanceof Error ? error.message : "Unknown entity load failure.",
          status: "error",
        });
      }
    }

    void loadEntities();

    return () => {
      abortController.abort();
    };
  }, [campaign.id]);

  return (
    <div className="campaign-entities-layout">
      <SectionPanel>
        <div className="section-actions">
          <Link className="primary-button" to={`/campaigns/${campaign.id}/entities/new`}>
            New Entity
          </Link>
        </div>
        {pageState.status === "loading" ? (
          <RequestStateBlock
            message="Loading this campaign's saved entities."
            title="Loading entities"
          />
        ) : null}
        {pageState.status === "error" ? (
          <RequestStateBlock
            message={pageState.message}
            title="Entities unavailable"
            tone="error"
          />
        ) : null}
        {pageState.status === "ready" && pageState.entities.length === 0 ? (
          <RequestStateBlock
            message="Add the first entity for this campaign from here to keep ownership context explicit."
            title="No campaign entities yet"
          />
        ) : null}
        {pageState.status === "ready" && pageState.entities.length > 0 ? (
          <CampaignEntityRoster entities={pageState.entities} onQuickLook={setSelectedEntity} />
        ) : null}
      </SectionPanel>
      {selectedEntity ? (
        <EntityQuickLookPanel
          campaign={campaign}
          entity={selectedEntity}
          onClose={() => {
            setSelectedEntity(null);
          }}
        />
      ) : null}
    </div>
  );
}
