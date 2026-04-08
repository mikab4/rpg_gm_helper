import { ENTITY_TYPE_OPTIONS } from "../entities/entityTypes";
import type { Campaign } from "../types/campaigns";

type EntityFiltersProps = {
  campaignId: string;
  campaigns: Campaign[];
  entitySearch: string;
  entityType: string;
  onCampaignIdChange: (value: string) => void;
  onEntitySearchChange: (value: string) => void;
  onEntityTypeChange: (value: string) => void;
};

export function EntityFilters({
  campaignId,
  campaigns,
  entitySearch,
  entityType,
  onCampaignIdChange,
  onEntitySearchChange,
  onEntityTypeChange,
}: EntityFiltersProps) {
  return (
    <div className="filter-grid">
      <label className="field">
        <span className="field-label">Search</span>
        <input
          placeholder="Find by entity name"
          type="text"
          value={entitySearch}
          onChange={(event) => {
            onEntitySearchChange(event.target.value);
          }}
        />
      </label>
      <label className="field">
        <span className="field-label">Campaign</span>
        <select
          value={campaignId}
          onChange={(event) => {
            onCampaignIdChange(event.target.value);
          }}
        >
          <option value="">All campaigns</option>
          {campaigns.map((campaign) => (
            <option key={campaign.id} value={campaign.id}>
              {campaign.name}
            </option>
          ))}
        </select>
      </label>
      <label className="field">
        <span className="field-label">Entity Type</span>
        <select
          value={entityType}
          onChange={(event) => {
            onEntityTypeChange(event.target.value);
          }}
        >
          <option value="">All entity types</option>
          {ENTITY_TYPE_OPTIONS.map((entityTypeOption) => (
            <option key={entityTypeOption.value} value={entityTypeOption.value}>
              {entityTypeOption.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
