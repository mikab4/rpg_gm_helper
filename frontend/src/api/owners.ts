import { apiRequest } from "./client";
import type { Owner } from "../types/owners";

type GetDefaultOwnerOptions = {
  signal?: AbortSignal;
};

function parseOwner(payload: unknown): Owner {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("id" in payload) ||
    typeof payload.id !== "string" ||
    !("email" in payload) ||
    !(typeof payload.email === "string" || payload.email === null) ||
    !("display_name" in payload) ||
    !(typeof payload.display_name === "string" || payload.display_name === null) ||
    !("created_at" in payload) ||
    typeof payload.created_at !== "string" ||
    !("updated_at" in payload) ||
    typeof payload.updated_at !== "string"
  ) {
    throw new Error("Invalid owner response payload.");
  }

  return {
    id: payload.id,
    email: payload.email,
    displayName: payload.display_name,
    createdAt: payload.created_at,
    updatedAt: payload.updated_at,
  };
}

export async function getDefaultOwner(options: GetDefaultOwnerOptions = {}): Promise<Owner> {
  const payload = await apiRequest("/owners/default", {
    signal: options.signal,
  });
  return parseOwner(payload);
}
