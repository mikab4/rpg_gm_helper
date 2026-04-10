from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from app.enums import EntityType
from app.schemas.entity_types import validate_entity_type
from app.schemas.types import NonBlankString, OptionalNonBlankString


class EntityCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: EntityType
    name: NonBlankString
    summary: OptionalNonBlankString = None
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("type", mode="before")
    @classmethod
    def validate_known_entity_type(cls, entity_type: str) -> EntityType:
        return validate_entity_type(entity_type)


class EntityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: EntityType | None = None
    name: OptionalNonBlankString = None
    summary: OptionalNonBlankString = None
    metadata: dict[str, object] | None = None

    @field_validator("type", mode="before")
    @classmethod
    def validate_known_entity_type(cls, entity_type: str | None) -> EntityType | None:
        if entity_type is None:
            return entity_type

        return validate_entity_type(entity_type)

    @model_validator(mode="after")
    def validate_entity_update_fields(self) -> "EntityUpdate":
        null_entity_type_update = self.type is None and "type" in self.model_fields_set
        null_entity_name_update = self.name is None and "name" in self.model_fields_set
        null_metadata_update = self.metadata is None and "metadata" in self.model_fields_set

        no_entity_type_update = "type" not in self.model_fields_set
        no_entity_name_update = "name" not in self.model_fields_set
        no_summary_update = self.summary is None and "summary" not in self.model_fields_set
        no_metadata_update = "metadata" not in self.model_fields_set

        if null_entity_type_update:
            raise ValueError("Entity type cannot be null.")

        if null_entity_name_update:
            raise ValueError("Entity name cannot be null.")

        if null_metadata_update:
            raise ValueError("Entity metadata cannot be null.")

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
    type: EntityType
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

    @field_serializer("type")
    def serialize_entity_type(self, entity_type: EntityType) -> str:
        return entity_type.value
