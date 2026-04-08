import { Link, Outlet, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import { getCampaign } from "../api/campaigns";
import { CampaignWorkspaceTabs } from "../components/CampaignWorkspaceTabs";
import { RequestStateBlock } from "../components/RequestStateBlock";
import type { Campaign } from "../types/campaigns";

type CampaignWorkspaceState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { campaign: Campaign; status: "ready" };

export type CampaignWorkspaceContext = {
  campaign: Campaign;
};

export function CampaignWorkspacePage() {
  const { campaignId } = useParams();
  const [pageState, setPageState] = useState<CampaignWorkspaceState>({ status: "loading" });

  useEffect(() => {
    const abortController = new AbortController();

    async function loadCampaign() {
      if (!campaignId) {
        setPageState({ message: "Campaign route is missing an identifier.", status: "error" });
        return;
      }

      try {
        const campaign = await getCampaign(campaignId, { signal: abortController.signal });
        setPageState({ campaign, status: "ready" });
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setPageState({
          message: error instanceof Error ? error.message : "Unknown campaign load failure.",
          status: "error",
        });
      }
    }

    void loadCampaign();

    return () => {
      abortController.abort();
    };
  }, [campaignId]);

  if (pageState.status === "loading") {
    return (
      <RequestStateBlock
        message="Loading the campaign workspace and its current details."
        title="Loading campaign"
      />
    );
  }

  if (pageState.status === "error") {
    return (
      <RequestStateBlock message={pageState.message} title="Campaign unavailable" tone="error" />
    );
  }

  return (
    <div className="page-stack workspace-surface">
      <div className="campaign-workspace-header">
        <Link className="campaign-back-link" to="/campaigns">
          Back to Registry
        </Link>
        <div className="campaign-workspace-heading">
          <h2 className="font-ui">{pageState.campaign.name}</h2>
        </div>
      </div>
      <CampaignWorkspaceTabs campaignId={pageState.campaign.id} />
      <Outlet context={{ campaign: pageState.campaign } satisfies CampaignWorkspaceContext} />
    </div>
  );
}
