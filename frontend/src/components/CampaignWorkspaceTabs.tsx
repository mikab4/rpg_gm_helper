import { NavLink } from "react-router-dom";

type CampaignWorkspaceTabsProps = {
  campaignId: string;
};

export function CampaignWorkspaceTabs({ campaignId }: CampaignWorkspaceTabsProps) {
  return (
    <nav aria-label="Campaign Sections" className="campaign-workspace-tabs">
      <NavLink
        className={({ isActive }) =>
          isActive
            ? "campaign-workspace-tab campaign-workspace-tab-active"
            : "campaign-workspace-tab"
        }
        end
        to={`/campaigns/${campaignId}`}
      >
        Overview
      </NavLink>
      <NavLink
        className={({ isActive }) =>
          isActive
            ? "campaign-workspace-tab campaign-workspace-tab-active"
            : "campaign-workspace-tab"
        }
        to={`/campaigns/${campaignId}/entities`}
      >
        Entities
      </NavLink>
    </nav>
  );
}
