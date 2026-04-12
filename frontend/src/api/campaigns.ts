import { apiRequest } from "./client";
import type { Campaign, CampaignCreate, CampaignUpdate } from "../types/campaigns";

type CampaignRequestOptions = {
  signal?: AbortSignal;
};

function parseCampaign(payload: unknown): Campaign {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("id" in payload) ||
    typeof payload.id !== "string" ||
    !("owner_id" in payload) ||
    typeof payload.owner_id !== "string" ||
    !("name" in payload) ||
    typeof payload.name !== "string" ||
    !("description" in payload) ||
    !(typeof payload.description === "string" || payload.description === null) ||
    !("created_at" in payload) ||
    typeof payload.created_at !== "string" ||
    !("updated_at" in payload) ||
    typeof payload.updated_at !== "string"
  ) {
    throw new Error("Invalid campaign response payload.");
  }

  return {
    id: payload.id,
    ownerId: payload.owner_id,
    name: payload.name,
    description: payload.description,
    createdAt: payload.created_at,
    updatedAt: payload.updated_at,
  };
}

function parseCampaignList(payload: unknown): Campaign[] {
  if (!Array.isArray(payload)) {
    throw new Error("Invalid campaign list response payload.");
  }

  return payload.map(parseCampaign);
}

function serializeCampaignCreate(campaignCreate: CampaignCreate): string {
  return JSON.stringify({
    owner_id: campaignCreate.ownerId,
    name: campaignCreate.name,
    description: campaignCreate.description,
  });
}

function serializeCampaignUpdate(campaignUpdate: CampaignUpdate): string {
  const payload: Record<string, string | null> = {};

  if (campaignUpdate.name !== undefined) {
    payload.name = campaignUpdate.name;
  }

  if (campaignUpdate.description !== undefined) {
    payload.description = campaignUpdate.description;
  }

  return JSON.stringify(payload);
}

export async function listCampaigns(options: CampaignRequestOptions = {}): Promise<Campaign[]> {
  const payload = await apiRequest("/campaigns", {
    signal: options.signal,
  });
  return parseCampaignList(payload);
}

export async function getCampaign(campaignId: string, options: CampaignRequestOptions = {}): Promise<Campaign> {
  const payload = await apiRequest(`/campaigns/${campaignId}`, {
    signal: options.signal,
  });
  return parseCampaign(payload);
}

export async function createCampaign(campaignCreate: CampaignCreate): Promise<Campaign> {
  const payload = await apiRequest("/campaigns", {
    body: serializeCampaignCreate(campaignCreate),
    headers: {
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  return parseCampaign(payload);
}

export async function updateCampaign(campaignId: string, campaignUpdate: CampaignUpdate): Promise<Campaign> {
  const payload = await apiRequest(`/campaigns/${campaignId}`, {
    body: serializeCampaignUpdate(campaignUpdate),
    headers: {
      "Content-Type": "application/json",
    },
    method: "PATCH",
  });

  return parseCampaign(payload);
}

export async function deleteCampaign(campaignId: string): Promise<void> {
  await apiRequest(`/campaigns/${campaignId}`, {
    method: "DELETE",
  });
}
