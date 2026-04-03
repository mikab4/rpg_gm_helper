import { apiRequest } from "./client";
import type { HealthResponse } from "../types/health";

type GetHealthOptions = {
  signal?: AbortSignal;
};

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

export async function getHealth(options: GetHealthOptions = {}): Promise<HealthResponse> {
  const payload = await apiRequest("/health", { signal: options.signal });

  return parseHealthResponse(payload);
}
