export type RelationshipType = {
  id: string | null;
  campaignId: string | null;
  key: string;
  label: string;
  family: string;
  reverseLabel: string | null;
  isSymmetric: boolean;
  allowedSourceTypes: string[];
  allowedTargetTypes: string[];
  isCustom: boolean;
  createdAt: string | null;
  updatedAt: string | null;
};

export type RelationshipTypeCreate = {
  label: string;
  family: string;
  reverseLabel: string | null;
  isSymmetric: boolean;
  allowedSourceTypes: string[];
  allowedTargetTypes: string[];
};

export type RelationshipTypeUpdate = {
  label?: string;
  family?: string;
  reverseLabel?: string | null;
  isSymmetric?: boolean;
  allowedSourceTypes?: string[];
  allowedTargetTypes?: string[];
};
