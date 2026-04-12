import type { LucideIcon } from "lucide-react";
import { BookOpen, Globe, LayoutDashboard, Map, ScanSearch, Search, Zap } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { applyEntityTypeMigration, getEntityTypeCompatibilityReport } from "../api/compatibility";
import { CompatibilityMigrationPanel } from "../components/CompatibilityMigrationPanel";
import type {
  EntityTypeCompatibilityReport,
  EntityTypeMigrationMapping,
  EntityTypeMigrationResult,
} from "../types/compatibility";

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

type CompatibilityState =
  | { status: "loading" }
  | { status: "error" }
  | { report: EntityTypeCompatibilityReport; status: "ready" };

export function AppShell() {
  const [compatibilityState, setCompatibilityState] = useState<CompatibilityState>({
    status: "loading",
  });
  const [migrationError, setMigrationError] = useState<string | null>(null);
  const [migrationResult, setMigrationResult] = useState<EntityTypeMigrationResult | null>(null);
  const [isMigrating, setIsMigrating] = useState(false);

  useEffect(() => {
    const abortController = new AbortController();

    async function loadCompatibilityReport() {
      try {
        const report = await getEntityTypeCompatibilityReport({ signal: abortController.signal });
        setCompatibilityState({ report, status: "ready" });
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setCompatibilityState({ status: "error" });
      }
    }

    void loadCompatibilityReport();

    return () => {
      abortController.abort();
    };
  }, []);

  async function handleApplyEntityTypeMigration(mappings: EntityTypeMigrationMapping[]): Promise<void> {
    setIsMigrating(true);
    setMigrationError(null);

    try {
      const result = await applyEntityTypeMigration(mappings);
      setMigrationResult(result);
      const report = await getEntityTypeCompatibilityReport();
      setCompatibilityState({ report, status: "ready" });
    } catch (error) {
      setMigrationError(error instanceof Error ? error.message : "Unknown migration failure.");
    } finally {
      setIsMigrating(false);
    }
  }

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
          {compatibilityState.status === "loading" ? (
            <section className="panel compatibility-panel compatibility-loading-panel">
              <h2 className="font-ui">Checking Data Compatibility</h2>
              <p>Reviewing stored entity types before opening the workspace.</p>
            </section>
          ) : null}
          {compatibilityState.status === "ready" && compatibilityState.report.hasIssues ? (
            <CompatibilityMigrationPanel
              migrationError={migrationError}
              migrationResult={migrationResult}
              report={compatibilityState.report}
              submitting={isMigrating}
              onSubmit={handleApplyEntityTypeMigration}
            />
          ) : null}
          {compatibilityState.status !== "loading" &&
          !(compatibilityState.status === "ready" && compatibilityState.report.hasIssues) ? (
            <Outlet />
          ) : null}
        </main>
      </div>
    </div>
  );
}
