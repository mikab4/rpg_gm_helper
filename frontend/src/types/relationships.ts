export type Relationship = {
  id: string;
  campaignId: string;
  sourceEntityId: string;
  targetEntityId: string;
  relationshipType: string;
  relationshipFamily: string;
  forwardLabel: string;
  reverseLabel: string;
  isSymmetric: boolean;
  lifecycleStatus: string;
  visibilityStatus: string;
  certaintyStatus: string;
  notes: string | null;
  confidence: number | null;
  sourceDocumentId: string | null;
  provenanceExcerpt: string | null;
  provenanceData: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
};

export type RelationshipCreate = {
  sourceEntityId: string;
  targetEntityId: string;
  relationshipType: string;
  lifecycleStatus: string;
  visibilityStatus: string;
  certaintyStatus: string;
  notes: string | null;
};

export type RelationshipUpdate = {
  relationshipType?: string;
  lifecycleStatus?: string;
  visibilityStatus?: string;
  certaintyStatus?: string;
  notes?: string | null;
};
