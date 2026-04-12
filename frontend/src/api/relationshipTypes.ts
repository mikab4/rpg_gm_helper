import { apiRequest } from "./client";
import { isEntityTypeValue } from "../entities/entityTypes";
import type { RelationshipType, RelationshipTypeCreate, RelationshipTypeUpdate } from "../types/relationshipTypes";

function parseRelationshipType(payload: unknown): RelationshipType {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("key" in payload) ||
    typeof payload.key !== "string" ||
    !("label" in payload) ||
    typeof payload.label !== "string" ||
    !("family" in payload) ||
    typeof payload.family !== "string" ||
    !("family_label" in payload) ||
    typeof payload.family_label !== "string" ||
    !("reverse_label" in payload) ||
    !(typeof payload.reverse_label === "string" || payload.reverse_label === null) ||
    !("is_symmetric" in payload) ||
    typeof payload.is_symmetric !== "boolean" ||
    !("allowed_source_types" in payload) ||
    !Array.isArray(payload.allowed_source_types) ||
    payload.allowed_source_types.some(
      (allowedSourceType) => typeof allowedSourceType !== "string" || !isEntityTypeValue(allowedSourceType),
    ) ||
    !("allowed_target_types" in payload) ||
    !Array.isArray(payload.allowed_target_types) ||
    payload.allowed_target_types.some(
      (allowedTargetType) => typeof allowedTargetType !== "string" || !isEntityTypeValue(allowedTargetType),
    ) ||
    !("is_custom" in payload) ||
    typeof payload.is_custom !== "boolean" ||
    !("created_at" in payload) ||
    !(typeof payload.created_at === "string" || payload.created_at === null) ||
    !("updated_at" in payload) ||
    !(typeof payload.updated_at === "string" || payload.updated_at === null)
  ) {
    throw new Error("Invalid relationship type response payload.");
  }

  const typedPayload = payload as {
    allowed_source_types: RelationshipType["allowedSourceTypes"];
    allowed_target_types: RelationshipType["allowedTargetTypes"];
    created_at: string | null;
    family: RelationshipType["family"];
    family_label: string;
    is_custom: boolean;
    is_symmetric: boolean;
    key: string;
    label: string;
    reverse_label: string | null;
    updated_at: string | null;
  } & {
    campaign_id?: string | null;
    id?: string | null;
  };

  return {
    id: "id" in typedPayload ? (typedPayload.id ?? null) : null,
    campaignId: "campaign_id" in typedPayload ? (typedPayload.campaign_id ?? null) : null,
    key: typedPayload.key,
    label: typedPayload.label,
    family: typedPayload.family,
    familyLabel: typedPayload.family_label,
    reverseLabel: typedPayload.reverse_label,
    isSymmetric: typedPayload.is_symmetric,
    allowedSourceTypes: typedPayload.allowed_source_types,
    allowedTargetTypes: typedPayload.allowed_target_types,
    isCustom: typedPayload.is_custom,
    createdAt: typedPayload.created_at,
    updatedAt: typedPayload.updated_at,
  };
}

function parseRelationshipTypeList(payload: unknown): RelationshipType[] {
  if (!Array.isArray(payload)) {
    throw new Error("Invalid relationship type list response payload.");
  }

  return payload.map(parseRelationshipType);
}

function serializeRelationshipTypeCreate(relationshipTypeCreate: RelationshipTypeCreate): string {
  return JSON.stringify({
    label: relationshipTypeCreate.label,
    family: relationshipTypeCreate.family,
    reverse_label: relationshipTypeCreate.reverseLabel,
    is_symmetric: relationshipTypeCreate.isSymmetric,
    allowed_source_types: relationshipTypeCreate.allowedSourceTypes,
    allowed_target_types: relationshipTypeCreate.allowedTargetTypes,
  });
}

function serializeRelationshipTypeUpdate(relationshipTypeUpdate: RelationshipTypeUpdate): string {
  const payload: Record<string, boolean | string | string[] | null> = {};

  if (relationshipTypeUpdate.label !== undefined) {
    payload.label = relationshipTypeUpdate.label;
  }
  if (relationshipTypeUpdate.family !== undefined) {
    payload.family = relationshipTypeUpdate.family;
  }
  if (relationshipTypeUpdate.reverseLabel !== undefined) {
    payload.reverse_label = relationshipTypeUpdate.reverseLabel;
  }
  if (relationshipTypeUpdate.isSymmetric !== undefined) {
    payload.is_symmetric = relationshipTypeUpdate.isSymmetric;
  }
  if (relationshipTypeUpdate.allowedSourceTypes !== undefined) {
    payload.allowed_source_types = relationshipTypeUpdate.allowedSourceTypes;
  }
  if (relationshipTypeUpdate.allowedTargetTypes !== undefined) {
    payload.allowed_target_types = relationshipTypeUpdate.allowedTargetTypes;
  }

  return JSON.stringify(payload);
}

export async function listRelationshipTypes(campaignId: string): Promise<RelationshipType[]> {
  const payload = await apiRequest(`/relationship-types?campaign_id=${campaignId}`);
  return parseRelationshipTypeList(payload);
}

export async function createRelationshipType(
  campaignId: string,
  relationshipTypeCreate: RelationshipTypeCreate,
): Promise<RelationshipType> {
  const payload = await apiRequest(`/campaigns/${campaignId}/relationship-types`, {
    body: serializeRelationshipTypeCreate(relationshipTypeCreate),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });
  return parseRelationshipType(payload);
}

export async function updateRelationshipType(
  campaignId: string,
  relationshipTypeKey: string,
  relationshipTypeUpdate: RelationshipTypeUpdate,
): Promise<RelationshipType> {
  const payload = await apiRequest(`/campaigns/${campaignId}/relationship-types/${relationshipTypeKey}`, {
    body: serializeRelationshipTypeUpdate(relationshipTypeUpdate),
    headers: { "Content-Type": "application/json" },
    method: "PATCH",
  });
  return parseRelationshipType(payload);
}

export async function deleteRelationshipType(campaignId: string, relationshipTypeKey: string): Promise<void> {
  await apiRequest(`/campaigns/${campaignId}/relationship-types/${relationshipTypeKey}`, {
    method: "DELETE",
  });
}
