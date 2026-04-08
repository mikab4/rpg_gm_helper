import { Link } from "react-router-dom";

import { formatEntityTypeLabel } from "../entities/entityTypes";
import type { Campaign } from "../types/campaigns";
import type { Entity } from "../types/entities";

type EntityQuickLookPanelProps = {
  entity: Entity;
  campaign?: Campaign;
  onClose: () => void;
};

export function EntityQuickLookPanel({ entity, campaign, onClose }: EntityQuickLookPanelProps) {
  return (
    <aside aria-label="Entity quick look" className="quick-look-panel quick-look-panel-paper">
      <div className="quick-look-header">
        <div>
          <p className="eyebrow">{formatEntityTypeLabel(entity.type)}</p>
          <h3>{entity.name}</h3>
        </div>
        <button className="icon-button" type="button" onClick={onClose}>
          Close
        </button>
      </div>
      <div className="quick-look-body">
        <section className="quick-look-section">
          <h4>Core Details</h4>
          <p>{formatEntityTypeLabel(entity.type)}</p>
        </section>
        <section className="quick-look-section">
          <h4>Summary</h4>
          <p>{entity.summary ?? "No summary recorded yet."}</p>
        </section>
        <section className="quick-look-section">
          <h4>Appears In</h4>
          <p>{campaign?.name ?? entity.campaignId}</p>
        </section>
      </div>
      <div className="quick-look-actions">
        <Link
          className="secondary-button"
          to={`/campaigns/${entity.campaignId}/entities/${entity.id}`}
        >
          Full Profile
        </Link>
        <Link
          className="primary-button"
          to={`/campaigns/${entity.campaignId}/entities/${entity.id}/edit`}
        >
          Edit Entity
        </Link>
      </div>
    </aside>
  );
}
