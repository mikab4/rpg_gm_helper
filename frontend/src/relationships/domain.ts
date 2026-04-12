export const RELATIONSHIP_FAMILY_OPTIONS = [
  { label: "Family", value: "family" },
  { label: "Romance", value: "romance" },
  { label: "Social", value: "social" },
  { label: "Organization", value: "organization" },
  { label: "Political", value: "political" },
  { label: "Location", value: "location" },
  { label: "Conflict", value: "conflict" },
  { label: "Influence", value: "influence" },
  { label: "Event", value: "event" },
] as const;

export const RELATIONSHIP_LIFECYCLE_STATUS_OPTIONS = [
  { label: "Current", value: "current" },
  { label: "Former", value: "former" },
] as const;

export const RELATIONSHIP_VISIBILITY_STATUS_OPTIONS = [
  { label: "Public", value: "public" },
  { label: "Secret", value: "secret" },
] as const;

export const RELATIONSHIP_CERTAINTY_STATUS_OPTIONS = [
  { label: "Confirmed", value: "confirmed" },
  { label: "Rumored", value: "rumored" },
] as const;

export type RelationshipFamilyValue = (typeof RELATIONSHIP_FAMILY_OPTIONS)[number]["value"];
export type RelationshipLifecycleStatusValue = (typeof RELATIONSHIP_LIFECYCLE_STATUS_OPTIONS)[number]["value"];
export type RelationshipVisibilityStatusValue = (typeof RELATIONSHIP_VISIBILITY_STATUS_OPTIONS)[number]["value"];
export type RelationshipCertaintyStatusValue = (typeof RELATIONSHIP_CERTAINTY_STATUS_OPTIONS)[number]["value"];

const RELATIONSHIP_FAMILY_VALUES = new Set<RelationshipFamilyValue>(
  RELATIONSHIP_FAMILY_OPTIONS.map((option) => option.value),
);
const RELATIONSHIP_LIFECYCLE_STATUS_VALUES = new Set<RelationshipLifecycleStatusValue>(
  RELATIONSHIP_LIFECYCLE_STATUS_OPTIONS.map((option) => option.value),
);
const RELATIONSHIP_VISIBILITY_STATUS_VALUES = new Set<RelationshipVisibilityStatusValue>(
  RELATIONSHIP_VISIBILITY_STATUS_OPTIONS.map((option) => option.value),
);
const RELATIONSHIP_CERTAINTY_STATUS_VALUES = new Set<RelationshipCertaintyStatusValue>(
  RELATIONSHIP_CERTAINTY_STATUS_OPTIONS.map((option) => option.value),
);

export function isRelationshipFamilyValue(relationshipFamily: string): relationshipFamily is RelationshipFamilyValue {
  return RELATIONSHIP_FAMILY_VALUES.has(relationshipFamily as RelationshipFamilyValue);
}

export function isRelationshipLifecycleStatusValue(
  relationshipLifecycleStatus: string,
): relationshipLifecycleStatus is RelationshipLifecycleStatusValue {
  return RELATIONSHIP_LIFECYCLE_STATUS_VALUES.has(relationshipLifecycleStatus as RelationshipLifecycleStatusValue);
}

export function isRelationshipVisibilityStatusValue(
  relationshipVisibilityStatus: string,
): relationshipVisibilityStatus is RelationshipVisibilityStatusValue {
  return RELATIONSHIP_VISIBILITY_STATUS_VALUES.has(relationshipVisibilityStatus as RelationshipVisibilityStatusValue);
}

export function isRelationshipCertaintyStatusValue(
  relationshipCertaintyStatus: string,
): relationshipCertaintyStatus is RelationshipCertaintyStatusValue {
  return RELATIONSHIP_CERTAINTY_STATUS_VALUES.has(relationshipCertaintyStatus as RelationshipCertaintyStatusValue);
}

export function formatRelationshipFamilyLabel(relationshipFamily: string): string {
  return (
    RELATIONSHIP_FAMILY_OPTIONS.find((option) => option.value === relationshipFamily)?.label ??
    relationshipFamily
      .split(/[_-]/)
      .filter(Boolean)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  );
}
