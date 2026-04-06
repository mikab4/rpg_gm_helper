from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.schemas.types import NonBlankString, OptionalNonBlankString


class EntityCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: NonBlankString
    name: NonBlankString
    summary: OptionalNonBlankString = None
    metadata: dict[str, object] = Field(default_factory=dict)


class EntityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: OptionalNonBlankString = None
    name: OptionalNonBlankString = None
    summary: OptionalNonBlankString = None
    metadata: dict[str, object] | None = None

    @model_validator(mode="after")
    def validate_entity_update_fields(self) -> "EntityUpdate":
        no_entity_type_update = self.type is None
        no_entity_name_update = self.name is None
        no_summary_update = self.summary is None and "summary" not in self.model_fields_set
        no_metadata_update = self.metadata is None

        if (
            no_entity_type_update
            and no_entity_name_update
            and no_summary_update
            and no_metadata_update
        ):
            raise ValueError("At least one entity field must be provided.")

        return self


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
