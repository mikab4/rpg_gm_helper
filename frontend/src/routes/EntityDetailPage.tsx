import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import { getCampaign } from "../api/campaigns";
import { getEntity } from "../api/entities";
import { PageHeader } from "../components/PageHeader";
import { RequestStateBlock } from "../components/RequestStateBlock";
import { SectionPanel } from "../components/SectionPanel";
import { formatEntityTypeLabel } from "../entities/entityTypes";
import type { Campaign } from "../types/campaigns";
import type { Entity } from "../types/entities";

type EntityDetailState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { campaign: Campaign; entity: Entity; status: "ready" };

export function EntityDetailPage() {
  const { campaignId, entityId } = useParams();
  const [pageState, setPageState] = useState<EntityDetailState>({ status: "loading" });

  useEffect(() => {
    const abortController = new AbortController();

    async function loadRecord() {
      if (!campaignId || !entityId) {
        setPageState({ message: "Entity route is missing identifiers.", status: "error" });
        return;
      }

      try {
        const [campaign, entity] = await Promise.all([
          getCampaign(campaignId, { signal: abortController.signal }),
          getEntity(campaignId, entityId, abortController.signal),
        ]);
        setPageState({ campaign, entity, status: "ready" });
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

    void loadRecord();

    return () => {
      abortController.abort();
    };
  }, [campaignId, entityId]);

  if (pageState.status === "loading") {
    return (
      <RequestStateBlock
        message="Loading entity details and campaign context."
        title="Loading entity"
      />
    );
  }

  if (pageState.status === "error") {
    return (
      <RequestStateBlock message={pageState.message} title="Entity unavailable" tone="error" />
    );
  }

  return (
    <div className="page-stack workspace-surface">
      <PageHeader
        actions={
          <div className="action-row">
            <Link className="secondary-button" to={`/campaigns/${pageState.campaign.id}/entities`}>
              Back To Campaign
            </Link>
            <Link
              className="primary-button"
              to={`/campaigns/${pageState.campaign.id}/entities/${pageState.entity.id}/edit`}
            >
              Edit Entity
            </Link>
          </div>
        }
        description={`Campaign: ${pageState.campaign.name}`}
        eyebrow={formatEntityTypeLabel(pageState.entity.type)}
        title={pageState.entity.name}
      />
      <div className="entity-page-grid">
        <SectionPanel title="Summary">
          <p>{pageState.entity.summary ?? "No summary recorded yet."}</p>
        </SectionPanel>
        <SectionPanel title="Record Details">
          <dl className="detail-list detail-list-compact">
            <div>
              <dt>Type</dt>
              <dd>{formatEntityTypeLabel(pageState.entity.type)}</dd>
            </div>
            <div>
              <dt>Appears In</dt>
              <dd>{pageState.campaign.name}</dd>
            </div>
            <div>
              <dt>Last Updated</dt>
              <dd>{new Date(pageState.entity.updatedAt).toLocaleString()}</dd>
            </div>
          </dl>
        </SectionPanel>
      </div>
    </div>
  );
}
