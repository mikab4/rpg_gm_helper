import { Link, Outlet, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import { deleteCampaign, getCampaign } from "../api/campaigns";
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

type CampaignDeleteState = { status: "idle" } | { campaignName: string; status: "deleted" };

export function CampaignWorkspacePage() {
  const { campaignId } = useParams();
  const [pageState, setPageState] = useState<CampaignWorkspaceState>({ status: "loading" });
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deleteState, setDeleteState] = useState<CampaignDeleteState>({ status: "idle" });
  const [deleting, setDeleting] = useState(false);

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

  async function handleDelete() {
    if (pageState.status !== "ready" || deleting) {
      return;
    }

    setDeleting(true);
    setDeleteError(null);

    try {
      await deleteCampaign(pageState.campaign.id);
      setDeleteState({ campaignName: pageState.campaign.name, status: "deleted" });
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : "Unknown campaign delete failure.");
    } finally {
      setDeleting(false);
    }
  }

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

  if (deleteState.status === "deleted") {
    return (
      <div className="page-stack workspace-surface">
        <RequestStateBlock
          message={`${deleteState.campaignName} has been removed from the campaign list.`}
          title="Campaign deleted"
        />
        <div className="action-row">
          <Link className="secondary-button" to="/campaigns">
            Back to Campaigns
          </Link>
        </div>
      </div>
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
        <div className="action-row">
          <Link className="secondary-button" to={`/campaigns/${pageState.campaign.id}/edit`}>
            Edit Campaign
          </Link>
          <button
            className="danger-button"
            disabled={deleting}
            type="button"
            onClick={() => void handleDelete()}
          >
            {deleting ? "Deleting..." : "Delete Campaign"}
          </button>
        </div>
      </div>
      {deleteError ? <p className="field-error">{deleteError}</p> : null}
      <CampaignWorkspaceTabs campaignId={pageState.campaign.id} />
      <Outlet context={{ campaign: pageState.campaign } satisfies CampaignWorkspaceContext} />
    </div>
  );
}
