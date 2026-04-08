export type Entity = {
  id: string;
  campaignId: string;
  type: string;
  name: string;
  summary: string | null;
  metadata: Record<string, unknown>;
  sourceDocumentId: string | null;
  provenanceExcerpt: string | null;
  provenanceData: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
};

export type EntityCreate = {
  type: string;
  name: string;
  summary: string | null;
  metadata: Record<string, unknown>;
};

export type EntityUpdate = {
  type?: string;
  name?: string;
  summary?: string | null;
  metadata?: Record<string, unknown>;
};
