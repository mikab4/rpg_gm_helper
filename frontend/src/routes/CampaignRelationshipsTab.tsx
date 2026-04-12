import { Link, useOutletContext, useSearchParams } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";

import { listCampaignEntities } from "../api/entities";
import { listRelationships } from "../api/relationships";
import { RequestStateBlock } from "../components/RequestStateBlock";
import { SectionPanel } from "../components/SectionPanel";
import { buildEntityNameMap, buildRelationshipPhrase, formatRelationshipStatus } from "../relationships/presentation";
import type { Entity } from "../types/entities";
import type { Relationship } from "../types/relationships";
import type { CampaignWorkspaceContext } from "./CampaignWorkspacePage";

type RelationshipTabState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { entities: Entity[]; relationships: Relationship[]; status: "ready" };

export function CampaignRelationshipsTab() {
  const { campaign } = useOutletContext<CampaignWorkspaceContext>();
  const [searchParams, setSearchParams] = useSearchParams();
  const [relationshipState, setRelationshipState] = useState<RelationshipTabState>({
    status: "loading",
  });
  const selectedEntityId = searchParams.get("entityId");

  useEffect(() => {
    const abortController = new AbortController();

    async function loadRelationships() {
      try {
        const [entities, relationships] = await Promise.all([
          listCampaignEntities(campaign.id, undefined, abortController.signal),
          listRelationships(campaign.id, { signal: abortController.signal }),
        ]);
        setRelationshipState({ entities, relationships, status: "ready" });
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setRelationshipState({
          message: error instanceof Error ? error.message : "Unknown relationship load failure.",
          status: "error",
        });
      }
    }

    void loadRelationships();

    return () => {
      abortController.abort();
    };
  }, [campaign.id]);

  const entitiesById = useMemo(
    () =>
      relationshipState.status === "ready" ? buildEntityNameMap(relationshipState.entities) : new Map<string, Entity>(),
    [relationshipState],
  );

  const visibleRelationships =
    relationshipState.status === "ready" && selectedEntityId
      ? relationshipState.relationships.filter(
          (relationship) =>
            relationship.sourceEntityId === selectedEntityId || relationship.targetEntityId === selectedEntityId,
        )
      : relationshipState.status === "ready"
        ? relationshipState.relationships
        : [];

  function handleEntityFilterChange(entityId: string) {
    if (!entityId) {
      setSearchParams({});
      return;
    }

    setSearchParams({ entityId });
  }

  return (
    <div className="page-stack">
      <SectionPanel title="Relationships">
        <div className="section-actions">
          <Link className="primary-button" to={`/campaigns/${campaign.id}/relationships/new`}>
            New Relationship
          </Link>
          <Link className="secondary-button" to={`/campaigns/${campaign.id}/relationship-types`}>
            New Relationship Type
          </Link>
        </div>
        {relationshipState.status === "loading" ? (
          <RequestStateBlock message="Loading campaign relationship records." title="Loading relationships" />
        ) : null}
        {relationshipState.status === "error" ? (
          <RequestStateBlock message={relationshipState.message} title="Relationships unavailable" tone="error" />
        ) : null}
        {relationshipState.status === "ready" ? (
          <label className="field relationship-filter-field">
            <span className="field-label">Filter By Entity</span>
            <select
              aria-label="Filter by entity"
              value={selectedEntityId ?? ""}
              onChange={(event) => {
                handleEntityFilterChange(event.target.value);
              }}
            >
              <option value="">All entities</option>
              {relationshipState.entities.map((entity) => (
                <option key={entity.id} value={entity.id}>
                  {entity.name}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        {relationshipState.status === "ready" && visibleRelationships.length === 0 ? (
          <RequestStateBlock
            message="No relationships match the current campaign context yet."
            title="No relationships found"
          />
        ) : null}
        {relationshipState.status === "ready" && visibleRelationships.length > 0 ? (
          <div className="relationship-list">
            {visibleRelationships.map((relationship) => (
              <article key={relationship.id} className="relationship-card">
                <div className="relationship-card-copy">
                  <strong>{buildRelationshipPhrase(relationship, entitiesById)}</strong>
                  <span>
                    {formatRelationshipStatus(relationship.lifecycleStatus)} ·{" "}
                    {formatRelationshipStatus(relationship.visibilityStatus)} ·{" "}
                    {formatRelationshipStatus(relationship.certaintyStatus)}
                  </span>
                  {relationship.notes ? <p>{relationship.notes}</p> : null}
                </div>
                <div className="relationship-card-actions">
                  <Link className="text-link" to={`/campaigns/${campaign.id}/relationships/${relationship.id}/edit`}>
                    Edit
                  </Link>
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </SectionPanel>
    </div>
  );
}
