export type LegacyEntityTypeExample = {
  entityId: string;
  entityName: string;
  campaignId: string;
  campaignName: string;
};

export type LegacyEntityTypeIssue = {
  legacyType: string;
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
  targetType: string;
};

export type EntityTypeMigrationResultItem = {
  legacyType: string;
  targetType: string;
  updatedCount: number;
};

export type EntityTypeMigrationResult = {
  updatedCount: number;
  updatedTypes: EntityTypeMigrationResultItem[];
};
