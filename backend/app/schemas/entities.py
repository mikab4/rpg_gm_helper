from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EntityCreate(BaseModel):
    campaign_id: UUID
    type: str
    name: str
    summary: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class EntityUpdate(BaseModel):
    type: str | None = None
    name: str | None = None
    summary: str | None = None
    metadata: dict[str, object] | None = None


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    type: str
    name: str
    summary: str | None
    metadata: dict[str, object] = Field(
        validation_alias="metadata_",
        serialization_alias="metadata",
    )
    source_document_id: UUID | None
    provenance_excerpt: str | None
    provenance_data: dict[str, object]
    created_at: datetime
    updated_at: datetime
