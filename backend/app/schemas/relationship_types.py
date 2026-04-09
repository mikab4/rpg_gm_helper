from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.schemas.entity_types import validate_entity_type, validate_entity_types
from app.schemas.types import NonBlankString, OptionalNonBlankString

ALLOWED_RELATIONSHIP_FAMILIES = {
    "family",
    "romance",
    "social",
    "organization",
    "political",
    "location",
    "conflict",
    "influence",
    "event",
}

_relationship_key_pattern = re.compile(r"[^a-z0-9]+")


def normalize_relationship_type_key(raw_label: str) -> str:
    normalized_label = raw_label.strip().lower()
    normalized_key = _relationship_key_pattern.sub("_", normalized_label).strip("_")
    if not normalized_key:
        raise ValueError("Relationship type label must include letters or numbers.")
    return normalized_key


def validate_relationship_family(relationship_family: str) -> str:
    normalized_family = relationship_family.strip().lower()
    if normalized_family not in ALLOWED_RELATIONSHIP_FAMILIES:
        allowed_values = ", ".join(sorted(ALLOWED_RELATIONSHIP_FAMILIES))
        raise ValueError(f"Relationship family must be one of: {allowed_values}.")
    return normalized_family


def validate_status_value(
    raw_status_value: str,
    *,
    allowed_values: set[str],
    field_name: str,
) -> str:
    normalized_status_value = raw_status_value.strip().lower()
    if normalized_status_value not in allowed_values:
        joined_allowed_values = ", ".join(sorted(allowed_values))
        raise ValueError(f"{field_name} must be one of: {joined_allowed_values}.")
    return normalized_status_value


class RelationshipTypeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: NonBlankString
    family: NonBlankString
    reverse_label: OptionalNonBlankString = None
    is_symmetric: bool
    allowed_source_types: list[str]
    allowed_target_types: list[str]

    @field_validator("family")
    @classmethod
    def validate_known_family(cls, relationship_family: str) -> str:
        return validate_relationship_family(relationship_family)

    @field_validator("allowed_source_types", "allowed_target_types")
    @classmethod
    def validate_allowed_entity_types(cls, entity_types: list[str]) -> list[str]:
        validate_entity_types(entity_types)
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
    family: OptionalNonBlankString = None
    reverse_label: OptionalNonBlankString = None
    is_symmetric: bool | None = None
    allowed_source_types: list[str] | None = None
    allowed_target_types: list[str] | None = None

    @field_validator("family")
    @classmethod
    def validate_known_family(cls, relationship_family: str | None) -> str | None:
        if relationship_family is None:
            return relationship_family
        return validate_relationship_family(relationship_family)

    @field_validator("allowed_source_types", "allowed_target_types")
    @classmethod
    def validate_allowed_entity_types(cls, entity_types: list[str] | None) -> list[str] | None:
        if entity_types is None:
            return entity_types
        validate_entity_types(entity_types)
        return [validate_entity_type(entity_type) for entity_type in entity_types]

    @model_validator(mode="after")
    def validate_update_fields(self) -> "RelationshipTypeUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one relationship type field must be provided.")
        return self


class RelationshipTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    campaign_id: UUID | None = None
    key: str
    label: str
    family: str
    reverse_label: str | None
    is_symmetric: bool
    allowed_source_types: list[str]
    allowed_target_types: list[str]
    is_custom: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
