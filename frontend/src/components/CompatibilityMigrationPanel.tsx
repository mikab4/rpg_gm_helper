import { useMemo, useState, type SyntheticEvent } from "react";

import type {
  EntityTypeCompatibilityReport,
  EntityTypeMigrationMapping,
  EntityTypeMigrationResult,
} from "../types/compatibility";

type CompatibilityMigrationPanelProps = {
  report: EntityTypeCompatibilityReport;
  migrationError: string | null;
  migrationResult: EntityTypeMigrationResult | null;
  submitting: boolean;
  onSubmit: (mappings: EntityTypeMigrationMapping[]) => Promise<void>;
};

const COMPATIBILITY_ENTITY_TYPE_OPTIONS = [
  {
    description: "People, characters, and named individuals",
    label: "Person",
    value: "person",
  },
  {
    description: "Places, regions, and physical settings",
    label: "Location",
    value: "location",
  },
  {
    description: "Groups, factions, and institutions",
    label: "Organization",
    value: "organization",
  },
  {
    description: "Objects, artifacts, and tangible things",
    label: "Item",
    value: "item",
  },
  {
    description: "Battles, rituals, and significant happenings",
    label: "Event",
    value: "event",
  },
  {
    description: "Gods, spirits, and divine powers",
    label: "Deity",
    value: "deity",
  },
  {
    description: "Anything that does not fit the main categories cleanly",
    label: "Other",
    value: "other",
  },
] as const;

const MIGRATION_VALUE_HINTS: Record<string, string> = {
  deity: "Using Deity keeps divine figures separate from ordinary characters in relationship views.",
  event: "Using Event helps the app connect causes, outcomes, and participants more clearly.",
  item: "Using Item makes artifacts and objects easier to track across ownership and discovery relationships.",
  location: "Using Location helps the app anchor places in travel, residence, and political relationships.",
  organization: "Using Organization helps the app track membership, leadership, and allegiance more accurately.",
  other: "Using Other preserves the record while keeping edge cases visible for later cleanup.",
  person: "Using Person helps the app track social, family, and political relationships more accurately.",
};

function getMigrationHint(selectedEntityType: string): string {
  if (!selectedEntityType) {
    return "Choosing the best match now gives the app a clearer foundation for future relationship tracking.";
  }

  return MIGRATION_VALUE_HINTS[selectedEntityType] ?? MIGRATION_VALUE_HINTS.other;
}

export function CompatibilityMigrationPanel({
  report,
  migrationError,
  migrationResult,
  submitting,
  onSubmit,
}: CompatibilityMigrationPanelProps) {
  const [mappingByLegacyType, setMappingByLegacyType] = useState<Record<string, string>>(() =>
    Object.fromEntries(report.issues.map((issue) => [issue.legacyType, ""])),
  );
  const [formError, setFormError] = useState<string | null>(null);

  const unresolvedLegacyTypes = useMemo(
    () => report.issues.filter((issue) => !mappingByLegacyType[issue.legacyType]),
    [mappingByLegacyType, report.issues],
  );

  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    if (unresolvedLegacyTypes.length > 0) {
      setFormError("Choose a canonical target type for every legacy entity type before applying.");
      return;
    }

    setFormError(null);
    await onSubmit(
      report.issues.map((issue) => ({
        legacyType: issue.legacyType,
        targetType: mappingByLegacyType[issue.legacyType],
      })),
    );
  }

  return (
    <section className="panel compatibility-panel">
      <div className="compatibility-copy compatibility-header">
        <h2 className="font-ui">Update Your Data Structure</h2>
        <p>
          We&apos;ve improved how our system handles relationships. To keep your information accurate, please tell us how to
          categorize these legacy labels.
        </p>
      </div>

      <form
        className="compatibility-form"
        onSubmit={(event) => {
          void handleSubmit(event);
        }}
      >
        {report.issues.map((issue) => (
          <section key={issue.legacyType} className="compatibility-issue">
            <div className="compatibility-issue-heading">
              <div className="compatibility-issue-copy">
                <h3>&quot;{issue.legacyType}&quot;</h3>
                <p>
                  {issue.count} affected record{issue.count === 1 ? "" : "s"}
                </p>
              </div>
              <span className="compatibility-badge">Legacy Type</span>
            </div>
            <label className="field compatibility-field">
              <span className="field-label">Move this to the new category</span>
              <select
                aria-label={`Map ${issue.legacyType} to`}
                value={mappingByLegacyType[issue.legacyType] ?? ""}
                onChange={(event) => {
                  setMappingByLegacyType((currentMappings) => ({
                    ...currentMappings,
                    [issue.legacyType]: event.target.value,
                  }));
                }}
              >
                <option value="">Select the best match...</option>
                {COMPATIBILITY_ENTITY_TYPE_OPTIONS.map((entityTypeOption) => (
                  <option key={entityTypeOption.value} value={entityTypeOption.value}>
                    {entityTypeOption.label} ({entityTypeOption.description})
                  </option>
                ))}
              </select>
            </label>
            <p className="compatibility-hint">{getMigrationHint(mappingByLegacyType[issue.legacyType] ?? "")}</p>
          </section>
        ))}

        <div className="compatibility-actions">
          {formError ? <p className="field-error">{formError}</p> : null}
          {migrationError ? <p className="field-error">{migrationError}</p> : null}
          {migrationResult ? (
            <p className="compatibility-success">
              Updated {migrationResult.updatedCount} record
              {migrationResult.updatedCount === 1 ? "" : "s"} across {migrationResult.updatedTypes.length} legacy type
              {migrationResult.updatedTypes.length === 1 ? "" : "s"}.
            </p>
          ) : null}
          <button className="primary-button compatibility-submit" disabled={submitting} type="submit">
            {submitting ? "Applying..." : "Update and Apply Changes"}
          </button>
          <p className="compatibility-warning">This process is permanent once applied. Please review your mappings.</p>
        </div>
      </form>
    </section>
  );
}
