import { apiRequest } from "./client";
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
    !("reverse_label" in payload) ||
    !(typeof payload.reverse_label === "string" || payload.reverse_label === null) ||
    !("is_symmetric" in payload) ||
    typeof payload.is_symmetric !== "boolean" ||
    !("allowed_source_types" in payload) ||
    !Array.isArray(payload.allowed_source_types) ||
    !("allowed_target_types" in payload) ||
    !Array.isArray(payload.allowed_target_types) ||
    !("is_custom" in payload) ||
    typeof payload.is_custom !== "boolean" ||
    !("created_at" in payload) ||
    !(typeof payload.created_at === "string" || payload.created_at === null) ||
    !("updated_at" in payload) ||
    !(typeof payload.updated_at === "string" || payload.updated_at === null)
  ) {
    throw new Error("Invalid relationship type response payload.");
  }

  return {
    id: "id" in payload && (typeof payload.id === "string" || payload.id === null) ? payload.id : null,
    campaignId:
      "campaign_id" in payload && (typeof payload.campaign_id === "string" || payload.campaign_id === null)
        ? payload.campaign_id
        : null,
    key: payload.key,
    label: payload.label,
    family: payload.family,
    reverseLabel: payload.reverse_label,
    isSymmetric: payload.is_symmetric,
    allowedSourceTypes: payload.allowed_source_types.map(String),
    allowedTargetTypes: payload.allowed_target_types.map(String),
    isCustom: payload.is_custom,
    createdAt: payload.created_at,
    updatedAt: payload.updated_at,
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
