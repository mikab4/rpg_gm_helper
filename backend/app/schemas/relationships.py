from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.relationship_types import validate_status_value
from app.schemas.types import NonBlankString, OptionalNonBlankString

ALLOWED_LIFECYCLE_STATUSES = {"current", "former"}
ALLOWED_VISIBILITY_STATUSES = {"public", "secret"}
ALLOWED_CERTAINTY_STATUSES = {"confirmed", "rumored"}


class RelationshipCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: NonBlankString
    lifecycle_status: NonBlankString
    visibility_status: NonBlankString
    certainty_status: NonBlankString
    notes: OptionalNonBlankString = None
    confidence: float | None = None
    source_document_id: UUID | None = None
    provenance_excerpt: OptionalNonBlankString = None
    provenance_data: dict[str, object] = Field(default_factory=dict)

    @field_validator("relationship_type")
    @classmethod
    def normalize_relationship_type(cls, relationship_type: str) -> str:
        return relationship_type.strip().lower()

    @field_validator("lifecycle_status")
    @classmethod
    def validate_lifecycle_status(cls, lifecycle_status: str) -> str:
        return validate_status_value(
            lifecycle_status,
            allowed_values=ALLOWED_LIFECYCLE_STATUSES,
            field_name="Lifecycle status",
        )

    @field_validator("visibility_status")
    @classmethod
    def validate_visibility_status(cls, visibility_status: str) -> str:
        return validate_status_value(
            visibility_status,
            allowed_values=ALLOWED_VISIBILITY_STATUSES,
            field_name="Visibility status",
        )

    @field_validator("certainty_status")
    @classmethod
    def validate_certainty_status(cls, certainty_status: str) -> str:
        return validate_status_value(
            certainty_status,
            allowed_values=ALLOWED_CERTAINTY_STATUSES,
            field_name="Certainty status",
        )

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, confidence: float | None) -> float | None:
        if confidence is None:
            return confidence
        if confidence < 0 or confidence > 1:
            raise ValueError("Relationship confidence must be between 0 and 1.")
        return confidence


class RelationshipUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationship_type: OptionalNonBlankString = None
    lifecycle_status: OptionalNonBlankString = None
    visibility_status: OptionalNonBlankString = None
    certainty_status: OptionalNonBlankString = None
    notes: OptionalNonBlankString = None
    confidence: float | None = None
    source_document_id: UUID | None = None
    provenance_excerpt: OptionalNonBlankString = None
    provenance_data: dict[str, object] | None = None

    @field_validator("relationship_type")
    @classmethod
    def normalize_relationship_type(cls, relationship_type: str | None) -> str | None:
        if relationship_type is None:
            return relationship_type
        return relationship_type.strip().lower()

    @field_validator("lifecycle_status")
    @classmethod
    def validate_lifecycle_status(cls, lifecycle_status: str | None) -> str | None:
        if lifecycle_status is None:
            return lifecycle_status
        return validate_status_value(
            lifecycle_status,
            allowed_values=ALLOWED_LIFECYCLE_STATUSES,
            field_name="Lifecycle status",
        )

    @field_validator("visibility_status")
    @classmethod
    def validate_visibility_status(cls, visibility_status: str | None) -> str | None:
        if visibility_status is None:
            return visibility_status
        return validate_status_value(
            visibility_status,
            allowed_values=ALLOWED_VISIBILITY_STATUSES,
            field_name="Visibility status",
        )

    @field_validator("certainty_status")
    @classmethod
    def validate_certainty_status(cls, certainty_status: str | None) -> str | None:
        if certainty_status is None:
            return certainty_status
        return validate_status_value(
            certainty_status,
            allowed_values=ALLOWED_CERTAINTY_STATUSES,
            field_name="Certainty status",
        )

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, confidence: float | None) -> float | None:
        if confidence is None:
            return confidence
        if confidence < 0 or confidence > 1:
            raise ValueError("Relationship confidence must be between 0 and 1.")
        return confidence

    @model_validator(mode="after")
    def validate_update_fields(self) -> "RelationshipUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one relationship field must be provided.")
        return self


class RelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=False)

    id: UUID
    campaign_id: UUID
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str
    relationship_family: str
    forward_label: str
    reverse_label: str
    is_symmetric: bool
    lifecycle_status: str
    visibility_status: str
    certainty_status: str
    notes: str | None
    confidence: float | None
    source_document_id: UUID | None
    provenance_excerpt: str | None
    provenance_data: dict[str, object]
    created_at: datetime
    updated_at: datetime
