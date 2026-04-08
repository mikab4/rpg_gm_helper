import type { LucideIcon } from "lucide-react";
import { BookOpen, Globe, LayoutDashboard, Map, ScanSearch, Search, Zap } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

interface NavigationItem {
  to: string;
  label: string;
  icon: LucideIcon;
  end?: boolean;
}

const navigationItems: NavigationItem[] = [
  { to: "/", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/campaigns", label: "Campaigns", icon: Map },
  { to: "/entities", label: "World", icon: Globe },
  { to: "/session-notes", label: "Session Notes", icon: BookOpen },
  { to: "/extraction-review", label: "Extraction", icon: ScanSearch },
  { to: "/search", label: "Search", icon: Search },
];

export function AppShell() {
  return (
    <div className="shell">
      <header className="shell-header">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">
            <Zap size={16} strokeWidth={2.2} />
          </div>
          <h1 className="font-cinzel">GM Workspace</h1>
        </div>
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
              <item.icon aria-hidden="true" size={15} strokeWidth={2} />
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
