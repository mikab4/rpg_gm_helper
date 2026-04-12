import { apiRequest } from "./client";
import type { RelationshipFamilyOption } from "../types/relationshipFamilies";

function parseRelationshipFamilyOption(payload: unknown): RelationshipFamilyOption {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("value" in payload) ||
    typeof payload.value !== "string" ||
    !("label" in payload) ||
    typeof payload.label !== "string"
  ) {
    throw new Error("Invalid relationship family response payload.");
  }

  return {
    label: payload.label,
    value: payload.value,
  };
}

function parseRelationshipFamilyList(payload: unknown): RelationshipFamilyOption[] {
  if (!Array.isArray(payload)) {
    throw new Error("Invalid relationship family list response payload.");
  }

  return payload.map(parseRelationshipFamilyOption);
}

export async function listRelationshipFamilies(): Promise<RelationshipFamilyOption[]> {
  const payload = await apiRequest("/relationship-families");
  return parseRelationshipFamilyList(payload);
}
