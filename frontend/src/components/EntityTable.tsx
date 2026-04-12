import { Link } from "react-router-dom";

import type { Campaign } from "../types/campaigns";
import type { Entity } from "../types/entities";

type EntityTableProps = {
  campaignsById?: Map<string, Campaign>;
  entities: Entity[];
  showCampaignColumn: boolean;
  onQuickLook?: (entity: Entity) => void;
};

export function EntityTable({
  campaignsById = new Map<string, Campaign>(),
  entities,
  showCampaignColumn,
  onQuickLook,
}: EntityTableProps) {
  return (
    <div className="table-shell">
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            {showCampaignColumn ? <th>Campaign</th> : null}
            <th>Known Relationships</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {entities.map((entity) => (
            <tr key={entity.id}>
              <td>
                <Link className="record-link" to={`/campaigns/${entity.campaignId}/entities/${entity.id}`}>
                  {entity.name}
                </Link>
              </td>
              <td>{entity.type}</td>
              {showCampaignColumn ? <td>{campaignsById.get(entity.campaignId)?.name ?? entity.campaignId}</td> : null}
              <td>{entity.summary ?? "No relationship scent recorded yet."}</td>
              <td>
                <Link className="text-link" to={`/campaigns/${entity.campaignId}/entities/${entity.id}`}>
                  Open
                </Link>
                {onQuickLook ? (
                  <button
                    className="text-button"
                    type="button"
                    onClick={() => {
                      onQuickLook(entity);
                    }}
                  >
                    Quick look {entity.name}
                  </button>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
