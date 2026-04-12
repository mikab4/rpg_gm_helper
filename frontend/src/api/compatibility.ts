import { apiRequest } from "./client";
import type {
  EntityTypeCompatibilityReport,
  EntityTypeMigrationMapping,
  EntityTypeMigrationResult,
  LegacyEntityTypeExample,
  LegacyEntityTypeIssue,
} from "../types/compatibility";

function parseLegacyEntityTypeExample(payload: unknown): LegacyEntityTypeExample {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("entity_id" in payload) ||
    typeof payload.entity_id !== "string" ||
    !("entity_name" in payload) ||
    typeof payload.entity_name !== "string" ||
    !("campaign_id" in payload) ||
    typeof payload.campaign_id !== "string" ||
    !("campaign_name" in payload) ||
    typeof payload.campaign_name !== "string"
  ) {
    throw new Error("Invalid legacy entity type example payload.");
  }

  return {
    campaignId: payload.campaign_id,
    campaignName: payload.campaign_name,
    entityId: payload.entity_id,
    entityName: payload.entity_name,
  };
}

function parseLegacyEntityTypeIssue(payload: unknown): LegacyEntityTypeIssue {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("legacy_type" in payload) ||
    typeof payload.legacy_type !== "string" ||
    !("raw_variants" in payload) ||
    !Array.isArray(payload.raw_variants) ||
    payload.raw_variants.some((rawVariant) => typeof rawVariant !== "string") ||
    !("count" in payload) ||
    typeof payload.count !== "number" ||
    !("example_entities" in payload) ||
    !Array.isArray(payload.example_entities)
  ) {
    throw new Error("Invalid legacy entity type issue payload.");
  }

  const typedPayload = payload as {
    legacy_type: string;
    raw_variants: string[];
    count: number;
    example_entities: unknown[];
  };

  return {
    legacyType: typedPayload.legacy_type,
    rawVariants: typedPayload.raw_variants,
    count: typedPayload.count,
    exampleEntities: typedPayload.example_entities.map(parseLegacyEntityTypeExample),
  };
}

function parseEntityTypeCompatibilityReport(payload: unknown): EntityTypeCompatibilityReport {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("has_issues" in payload) ||
    typeof payload.has_issues !== "boolean" ||
    !("issue_count" in payload) ||
    typeof payload.issue_count !== "number" ||
    !("issues" in payload) ||
    !Array.isArray(payload.issues)
  ) {
    throw new Error("Invalid entity type compatibility payload.");
  }

  return {
    hasIssues: payload.has_issues,
    issueCount: payload.issue_count,
    issues: payload.issues.map(parseLegacyEntityTypeIssue),
  };
}

function parseEntityTypeMigrationResult(payload: unknown): EntityTypeMigrationResult {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("updated_count" in payload) ||
    typeof payload.updated_count !== "number" ||
    !("updated_types" in payload) ||
    !Array.isArray(payload.updated_types)
  ) {
    throw new Error("Invalid entity type migration result payload.");
  }

  const typedPayload = payload as {
    updated_count: number;
    updated_types: unknown[];
  };

  return {
    updatedCount: typedPayload.updated_count,
    updatedTypes: typedPayload.updated_types.map((updatedTypePayload) => {
      if (
        typeof updatedTypePayload !== "object" ||
        updatedTypePayload === null ||
        !("legacy_type" in updatedTypePayload) ||
        typeof updatedTypePayload.legacy_type !== "string" ||
        !("target_type" in updatedTypePayload) ||
        typeof updatedTypePayload.target_type !== "string" ||
        !("updated_count" in updatedTypePayload) ||
        typeof updatedTypePayload.updated_count !== "number"
      ) {
        throw new Error("Invalid entity type migration result item payload.");
      }

      const typedUpdatedTypePayload = updatedTypePayload as {
        legacy_type: string;
        target_type: string;
        updated_count: number;
      };

      return {
        legacyType: typedUpdatedTypePayload.legacy_type,
        targetType: typedUpdatedTypePayload.target_type,
        updatedCount: typedUpdatedTypePayload.updated_count,
      };
    }),
  };
}

export async function getEntityTypeCompatibilityReport(
  options: { signal?: AbortSignal } = {},
): Promise<EntityTypeCompatibilityReport> {
  const payload = await apiRequest("/compatibility/entity-types", {
    signal: options.signal,
  });
  return parseEntityTypeCompatibilityReport(payload);
}

export async function applyEntityTypeMigration(mappings: EntityTypeMigrationMapping[]): Promise<EntityTypeMigrationResult> {
  const payload = await apiRequest("/compatibility/entity-types/migrate", {
    body: JSON.stringify({
      mappings: mappings.map((mapping) => ({
        legacy_type: mapping.legacyType,
        target_type: mapping.targetType,
      })),
    }),
    headers: {
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  return parseEntityTypeMigrationResult(payload);
}
