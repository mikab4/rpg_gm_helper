from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, model_validator

from app.enums import (
    EntityType,
    RelationshipFamily,
    format_relationship_family_label,
    normalize_str_enum_value,
)
from app.schemas.entity_types import validate_entity_type
from app.schemas.types import NonBlankString, OptionalNonBlankString

_relationship_key_pattern = re.compile(r"[^a-z0-9]+")


def normalize_relationship_type_key(raw_label: str) -> str:
    normalized_label = raw_label.strip().lower()
    normalized_key = _relationship_key_pattern.sub("_", normalized_label).strip("_")
    if not normalized_key:
        raise ValueError("Relationship type label must include letters or numbers.")
    return normalized_key


def validate_relationship_family(relationship_family: str) -> RelationshipFamily:
    return normalize_str_enum_value(RelationshipFamily, relationship_family)


class RelationshipTypeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: NonBlankString
    family: RelationshipFamily
    reverse_label: OptionalNonBlankString = None
    is_symmetric: bool
    allowed_source_types: list[EntityType]
    allowed_target_types: list[EntityType]

    @field_validator("family", mode="before")
    @classmethod
    def validate_known_family(cls, relationship_family: str) -> RelationshipFamily:
        return validate_relationship_family(relationship_family)

    @field_validator("allowed_source_types", "allowed_target_types", mode="before")
    @classmethod
    def validate_allowed_entity_types(cls, entity_types: list[str]) -> list[EntityType]:
        return [validate_entity_type(entity_type) for entity_type in entity_types]

    @model_validator(mode="after")
    def validate_direction_metadata(self) -> "RelationshipTypeCreate":
        if self.is_symmetric and self.reverse_label is not None:
            raise ValueError("Symmetric relationship types cannot define a reverse label.")
        if not self.is_symmetric and self.reverse_label is None:
            raise ValueError("Asymmetric relationship types must define a reverse label.")
        return self


class RelationshipTypeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: OptionalNonBlankString = None
    family: RelationshipFamily | None = None
    reverse_label: OptionalNonBlankString = None
    is_symmetric: bool | None = None
    allowed_source_types: list[EntityType] | None = None
    allowed_target_types: list[EntityType] | None = None

    @field_validator("family", mode="before")
    @classmethod
    def validate_known_family(
        cls,
        relationship_family: str | None,
    ) -> RelationshipFamily | None:
        if relationship_family is None:
            return relationship_family
        return validate_relationship_family(relationship_family)

    @field_validator("allowed_source_types", "allowed_target_types", mode="before")
    @classmethod
    def validate_allowed_entity_types(
        cls,
        entity_types: list[str] | None,
    ) -> list[EntityType] | None:
        if entity_types is None:
            return entity_types
        return [validate_entity_type(entity_type) for entity_type in entity_types]

    @model_validator(mode="after")
    def validate_update_fields(self) -> "RelationshipTypeUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one relationship type field must be provided.")
        if self.is_symmetric is True and self.reverse_label is not None:
            raise ValueError("Symmetric relationship types cannot define a reverse label.")
        return self


class RelationshipTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    campaign_id: UUID | None = None
    key: str
    label: str
    family: RelationshipFamily
    family_label: str
    reverse_label: str | None
    is_symmetric: bool
    allowed_source_types: list[EntityType]
    allowed_target_types: list[EntityType]
    is_custom: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_serializer("family")
    def serialize_family(self, relationship_family: RelationshipFamily) -> str:
        return relationship_family.value

    @field_serializer("allowed_source_types", "allowed_target_types")
    def serialize_allowed_entity_types(self, entity_types: list[EntityType]) -> list[str]:
        return [entity_type.value for entity_type in entity_types]


class RelationshipFamilyOptionResponse(BaseModel):
    value: RelationshipFamily
    label: str

    @field_serializer("value")
    def serialize_value(self, relationship_family: RelationshipFamily) -> str:
        return relationship_family.value

    @classmethod
    def from_relationship_family(
        cls,
        relationship_family: RelationshipFamily,
    ) -> "RelationshipFamilyOptionResponse":
        return cls(
            value=relationship_family,
            label=format_relationship_family_label(relationship_family),
        )
