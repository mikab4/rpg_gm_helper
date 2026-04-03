import { apiRequest } from "./client";
import type { HealthResponse } from "../types/health";

function parseHealthResponse(payload: unknown): HealthResponse {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("status" in payload) ||
    typeof payload.status !== "string"
  ) {
    throw new Error("Invalid health response payload.");
  }

  return {
    status: payload.status,
  };
}

export async function getHealth(): Promise<HealthResponse> {
  const payload = await apiRequest("/health");

  return parseHealthResponse(payload);
}
