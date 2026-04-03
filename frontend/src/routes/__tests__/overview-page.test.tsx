import { render, screen } from "@testing-library/react";
import { RouterProvider, createMemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { routes } from "../../app/routes";

describe("OverviewPage", () => {
  it("shows the connected backend status inside the app shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );

    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "RPG GM Helper" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Entities" })).toBeInTheDocument();
    expect(await screen.findByText("Connected")).toBeInTheDocument();
    expect(screen.getByText("Backend status: ok")).toBeInTheDocument();
  });

  it("shows an error state when the health response payload is invalid", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ state: "ok" }),
      }),
    );

    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByText("Unreachable")).toBeInTheDocument();
    expect(screen.getByText("Invalid health response payload.")).toBeInTheDocument();
  });
});
