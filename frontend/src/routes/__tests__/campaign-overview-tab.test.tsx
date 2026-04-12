import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { CampaignWorkspaceContext } from "../CampaignWorkspacePage";

const mockUseOutletContext = vi.fn<() => CampaignWorkspaceContext>();

function buildCampaignWorkspaceContext(
  campaignId: string,
  campaignName: string,
  campaignDescription: string,
): CampaignWorkspaceContext {
  return {
    campaign: {
      id: campaignId,
      ownerId: "owner-1",
      name: campaignName,
      description: campaignDescription,
      createdAt: "2026-04-08T12:00:00Z",
      updatedAt: "2026-04-08T12:00:00Z",
    },
  };
}

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    useOutletContext: () => mockUseOutletContext(),
  };
});

describe("CampaignOverviewTab", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it("persists quick notes for the active campaign", async () => {
    mockUseOutletContext.mockReturnValue(
      buildCampaignWorkspaceContext("campaign-1", "Shadows of Glass", "Urban intrigue campaign"),
    );

    const { CampaignOverviewTab } = await import("../CampaignOverviewTab");
    render(<CampaignOverviewTab />);

    fireEvent.change(screen.getByRole("textbox", { name: "Quick Notes" }), {
      target: { value: "Remember the king's brother knows the east gate signal." },
    });

    await waitFor(() => {
      expect(window.localStorage.getItem("gm-workspace:campaign-quick-notes:campaign-1")).toBe(
        "Remember the king's brother knows the east gate signal.",
      );
    });
  });

  it("does not overwrite another campaign's quick notes when the campaign context changes", async () => {
    window.localStorage.setItem("gm-workspace:campaign-quick-notes:campaign-2", "Campaign two already has notes.");

    let currentContext = buildCampaignWorkspaceContext("campaign-1", "Shadows of Glass", "Urban intrigue campaign");
    mockUseOutletContext.mockImplementation(() => currentContext);

    const { CampaignOverviewTab } = await import("../CampaignOverviewTab");
    const { rerender } = render(<CampaignOverviewTab />);

    fireEvent.change(screen.getByRole("textbox", { name: "Quick Notes" }), {
      target: { value: "Campaign one should keep its own note." },
    });

    await waitFor(() => {
      expect(window.localStorage.getItem("gm-workspace:campaign-quick-notes:campaign-1")).toBe(
        "Campaign one should keep its own note.",
      );
    });

    currentContext = buildCampaignWorkspaceContext("campaign-2", "Ashes of Karth", "Second campaign");

    rerender(<CampaignOverviewTab />);

    expect(await screen.findByRole("textbox", { name: "Quick Notes" })).toHaveValue("Campaign two already has notes.");
    expect(window.localStorage.getItem("gm-workspace:campaign-quick-notes:campaign-2")).toBe(
      "Campaign two already has notes.",
    );
  });
});
