import { createBrowserRouter, type RouteObject } from "react-router-dom";

import { AppShell } from "./AppShell";
import { CampaignEntitiesTab } from "../routes/CampaignEntitiesTab";
import { CampaignFormPage } from "../routes/CampaignFormPage";
import { CampaignOverviewTab } from "../routes/CampaignOverviewTab";
import { CampaignRelationshipsTab } from "../routes/CampaignRelationshipsTab";
import { CampaignWorkspacePage } from "../routes/CampaignWorkspacePage";
import { CampaignsPage } from "../routes/CampaignsPage";
import { EntitiesPage } from "../routes/EntitiesPage";
import { EntityDetailPage } from "../routes/EntityDetailPage";
import { EntityEditPage } from "../routes/EntityEditPage";
import { EntityFormPage } from "../routes/EntityFormPage";
import { OverviewPage } from "../routes/OverviewPage";
import { PlaceholderPage } from "../routes/PlaceholderPage";
import { RelationshipFormPage } from "../routes/RelationshipFormPage";
import { RelationshipTypeManagementPage } from "../routes/RelationshipTypeManagementPage";

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <AppShell />,
    children: [
      {
        index: true,
        element: <OverviewPage />,
      },
      {
        path: "campaigns",
        element: <CampaignsPage />,
      },
      {
        path: "campaigns/new",
        element: <CampaignFormPage mode="create" />,
      },
      {
        path: "campaigns/:campaignId",
        element: <CampaignWorkspacePage />,
        children: [
          {
            index: true,
            element: <CampaignOverviewTab />,
          },
          {
            path: "entities",
            element: <CampaignEntitiesTab />,
          },
          {
            path: "relationships",
            element: <CampaignRelationshipsTab />,
          },
        ],
      },
      {
        path: "campaigns/:campaignId/edit",
        element: <CampaignFormPage mode="edit" />,
      },
      {
        path: "campaigns/:campaignId/entities/new",
        element: <EntityFormPage source="campaign" />,
      },
      {
        path: "campaigns/:campaignId/entities/:entityId",
        element: <EntityDetailPage />,
      },
      {
        path: "campaigns/:campaignId/entities/:entityId/edit",
        element: <EntityEditPage />,
      },
      {
        path: "campaigns/:campaignId/relationships/new",
        element: <RelationshipFormPage mode="create" />,
      },
      {
        path: "campaigns/:campaignId/relationship-types",
        element: <RelationshipTypeManagementPage />,
      },
      {
        path: "campaigns/:campaignId/relationships/:relationshipId/edit",
        element: <RelationshipFormPage mode="edit" />,
      },
      {
        path: "entities",
        element: <EntitiesPage />,
      },
      {
        path: "entities/new",
        element: <EntityFormPage source="global" />,
      },
      {
        path: "session-notes",
        element: (
          <PlaceholderPage
            description="Session note ingestion and document flows will plug into this route after the backend slice is ready."
            title="Session Notes"
          />
        ),
      },
      {
        path: "extraction-review",
        element: (
          <PlaceholderPage
            description="Extraction candidates and review workflows will attach here once the extraction APIs are available."
            title="Extraction Review"
          />
        ),
      },
      {
        path: "search",
        element: (
          <PlaceholderPage
            description="Search scaffolding is routed now, but the real query surface waits on backend search endpoints."
            title="Search"
          />
        ),
      },
    ],
  },
];

export const router = createBrowserRouter(routes);
