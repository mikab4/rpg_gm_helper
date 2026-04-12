import type { EntityTypeValue } from "../entities/entityTypes";

export type LegacyEntityTypeExample = {
  entityId: string;
  entityName: string;
  campaignId: string;
  campaignName: string;
};

export type LegacyEntityTypeIssue = {
  legacyType: string;
  rawVariants: string[];
  count: number;
  exampleEntities: LegacyEntityTypeExample[];
};

export type EntityTypeCompatibilityReport = {
  hasIssues: boolean;
  issueCount: number;
  issues: LegacyEntityTypeIssue[];
};

export type EntityTypeMigrationMapping = {
  legacyType: string;
  targetType: EntityTypeValue;
};

export type EntityTypeMigrationResultItem = {
  legacyType: string;
  targetType: EntityTypeValue;
  updatedCount: number;
};

export type EntityTypeMigrationResult = {
  updatedCount: number;
  updatedTypes: EntityTypeMigrationResultItem[];
};
