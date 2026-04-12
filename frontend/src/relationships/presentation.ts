import type { Entity } from "../types/entities";
import type { Relationship } from "../types/relationships";
import { formatRelationshipFamilyLabel } from "./domain";

const IMPORTANT_RELATIONSHIP_TYPES = [
  "governs",
  "located_in",
  "lives_in",
  "based_in",
  "member_of",
  "leader_of",
  "parent_of",
  "child_of",
  "spouse_of",
  "sibling_of",
] as const;

export function buildEntityNameMap(entities: Entity[]): Map<string, Entity> {
  return new Map(entities.map((entity) => [entity.id, entity]));
}

export function formatRelationshipStatus(statusValue: string): string {
  return statusValue
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function buildRelationshipPhrase(
  relationship: Relationship,
  entitiesById: Map<string, Entity>,
  focusEntityId?: string,
): string {
  const sourceEntityName = entitiesById.get(relationship.sourceEntityId)?.name ?? "Unknown source";
  const targetEntityName = entitiesById.get(relationship.targetEntityId)?.name ?? "Unknown target";

  if (focusEntityId === relationship.targetEntityId && !relationship.isSymmetric) {
    return `${targetEntityName} ${relationship.reverseLabel} ${sourceEntityName}`;
  }

  return `${sourceEntityName} ${relationship.forwardLabel} ${targetEntityName}`;
}

export function buildImportantRelationshipPreview(
  entityId: string,
  relationships: Relationship[],
  entitiesById: Map<string, Entity>,
  limit: number,
): string[] {
  const relatedRelationships = relationships.filter(
    (relationship) => relationship.sourceEntityId === entityId || relationship.targetEntityId === entityId,
  );

  const prioritizedRelationships = [...relatedRelationships].sort((leftRelationship, rightRelationship) => {
    const leftPriority = IMPORTANT_RELATIONSHIP_TYPES.indexOf(
      leftRelationship.relationshipType as (typeof IMPORTANT_RELATIONSHIP_TYPES)[number],
    );
    const rightPriority = IMPORTANT_RELATIONSHIP_TYPES.indexOf(
      rightRelationship.relationshipType as (typeof IMPORTANT_RELATIONSHIP_TYPES)[number],
    );

    const normalizedLeftPriority = leftPriority === -1 ? IMPORTANT_RELATIONSHIP_TYPES.length : leftPriority;
    const normalizedRightPriority = rightPriority === -1 ? IMPORTANT_RELATIONSHIP_TYPES.length : rightPriority;

    return normalizedLeftPriority - normalizedRightPriority;
  });

  return prioritizedRelationships
    .slice(0, limit)
    .map((relationship) => buildRelationshipPhrase(relationship, entitiesById, entityId));
}

export function groupEntityRelationships(
  entityId: string,
  relationships: Relationship[],
  entitiesById: Map<string, Entity>,
): Array<{ family: string; phrases: string[] }> {
  const groupedRelationships = new Map<string, string[]>();

  for (const relationship of relationships) {
    if (relationship.sourceEntityId !== entityId && relationship.targetEntityId !== entityId) {
      continue;
    }

    const familyLabel = formatRelationshipFamilyLabel(relationship.relationshipFamily);
    const existingFamilyGroup = groupedRelationships.get(familyLabel) ?? [];
    existingFamilyGroup.push(buildRelationshipPhrase(relationship, entitiesById, entityId));
    groupedRelationships.set(familyLabel, existingFamilyGroup);
  }

  return Array.from(groupedRelationships.entries()).map(([family, phrases]) => ({
    family,
    phrases,
  }));
}
