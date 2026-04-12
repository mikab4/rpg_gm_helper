import { Link } from "react-router-dom";

import type { Campaign } from "../types/campaigns";

type CampaignTableProps = {
  campaigns: Campaign[];
};

export function CampaignTable({ campaigns }: CampaignTableProps) {
  return (
    <div className="campaign-card-list">
      {campaigns.map((campaign) => (
        <Link
          key={campaign.id}
          aria-label={`Open workspace for ${campaign.name}`}
          className="campaign-card"
          to={`/campaigns/${campaign.id}`}
        >
          <div className="campaign-card-copy">
            <h3 className="campaign-card-title">{campaign.name}</h3>
            <p className="campaign-card-updated">Last Updated {new Date(campaign.updatedAt).toLocaleDateString()}</p>
            <p className="campaign-card-description">{campaign.description ?? "No description yet."}</p>
          </div>
          <div aria-hidden="true" className="campaign-card-actions">
            <span className="campaign-card-open">
              <span aria-hidden="true">›</span>
            </span>
          </div>
        </Link>
      ))}
    </div>
  );
}
