import { NavLink, Outlet } from "react-router-dom";

interface NavigationItem {
  to: string;
  label: string;
  end?: boolean;
}

const navigationItems: NavigationItem[] = [
  { to: "/", label: "Overview", end: true },
  { to: "/campaigns", label: "Campaigns" },
  { to: "/entities", label: "Entities" },
  { to: "/session-notes", label: "Session Notes" },
  { to: "/extraction-review", label: "Extraction Review" },
  { to: "/search", label: "Search" },
];

export function AppShell() {
  return (
    <div className="shell">
      <header className="shell-header">
        <div>
          <p className="eyebrow">Local-First GM Workspace</p>
          <h1>RPG GM Helper</h1>
        </div>
        <p className="shell-copy">
          React routing is live, and the overview screen verifies backend connectivity through the
          current FastAPI health endpoint.
        </p>
      </header>
      <div className="shell-body">
        <nav aria-label="Primary" className="shell-nav">
          {navigationItems.map((item) => (
            <NavLink
              key={item.to}
              className={({ isActive }) => (isActive ? "nav-link nav-link-active" : "nav-link")}
              end={item.end}
              to={item.to}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <main className="shell-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
