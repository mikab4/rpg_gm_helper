import { createBrowserRouter, type RouteObject } from "react-router-dom";

import { AppShell } from "./AppShell";
import { OverviewPage } from "../routes/OverviewPage";
import { PlaceholderPage } from "../routes/PlaceholderPage";

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
        element: (
          <PlaceholderPage
            description="Campaign CRUD screens land here once the backend campaign endpoints are in place."
            title="Campaigns"
          />
        ),
      },
      {
        path: "entities",
        element: (
          <PlaceholderPage
            description="Entity CRUD stays out of the scaffold until backend contracts exist and can drive real client types."
            title="Entities"
          />
        ),
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
