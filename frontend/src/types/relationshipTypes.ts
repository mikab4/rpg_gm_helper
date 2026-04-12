import type { EntityTypeValue } from "../entities/entityTypes";
import type { RelationshipFamilyValue } from "../relationships/domain";

export type RelationshipType = {
  id: string | null;
  campaignId: string | null;
  key: string;
  label: string;
  family: RelationshipFamilyValue;
  reverseLabel: string | null;
  isSymmetric: boolean;
  allowedSourceTypes: EntityTypeValue[];
  allowedTargetTypes: EntityTypeValue[];
  isCustom: boolean;
  createdAt: string | null;
  updatedAt: string | null;
};

export type RelationshipTypeCreate = {
  label: string;
  family: RelationshipFamilyValue;
  reverseLabel: string | null;
  isSymmetric: boolean;
  allowedSourceTypes: EntityTypeValue[];
  allowedTargetTypes: EntityTypeValue[];
};

export type RelationshipTypeUpdate = {
  label?: string;
  family?: RelationshipFamilyValue;
  reverseLabel?: string | null;
  isSymmetric?: boolean;
  allowedSourceTypes?: EntityTypeValue[];
  allowedTargetTypes?: EntityTypeValue[];
};
