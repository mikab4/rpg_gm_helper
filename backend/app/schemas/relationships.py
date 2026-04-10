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

from app.enums import (
    RelationshipCertaintyStatus,
    RelationshipFamily,
    RelationshipLifecycleStatus,
    RelationshipVisibilityStatus,
    normalize_str_enum_value,
)
from app.schemas.types import NonBlankString, OptionalNonBlankString


class RelationshipCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: NonBlankString
    lifecycle_status: RelationshipLifecycleStatus
    visibility_status: RelationshipVisibilityStatus
    certainty_status: RelationshipCertaintyStatus
    notes: OptionalNonBlankString = None
    confidence: float | None = None
    source_document_id: UUID | None = None
    provenance_excerpt: OptionalNonBlankString = None
    provenance_data: dict[str, object] = Field(default_factory=dict)

    @field_validator("relationship_type")
    @classmethod
    def normalize_relationship_type(cls, relationship_type: str) -> str:
        return relationship_type.strip().lower()

    @field_validator("lifecycle_status", mode="before")
    @classmethod
    def validate_lifecycle_status(
        cls,
        lifecycle_status: str,
    ) -> RelationshipLifecycleStatus:
        return normalize_str_enum_value(
            RelationshipLifecycleStatus,
            lifecycle_status,
        )

    @field_validator("visibility_status", mode="before")
    @classmethod
    def validate_visibility_status(
        cls,
        visibility_status: str,
    ) -> RelationshipVisibilityStatus:
        return normalize_str_enum_value(
            RelationshipVisibilityStatus,
            visibility_status,
        )

    @field_validator("certainty_status", mode="before")
    @classmethod
    def validate_certainty_status(
        cls,
        certainty_status: str,
    ) -> RelationshipCertaintyStatus:
        return normalize_str_enum_value(
            RelationshipCertaintyStatus,
            certainty_status,
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
    lifecycle_status: RelationshipLifecycleStatus | None = None
    visibility_status: RelationshipVisibilityStatus | None = None
    certainty_status: RelationshipCertaintyStatus | None = None
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

    @field_validator("lifecycle_status", mode="before")
    @classmethod
    def validate_lifecycle_status(
        cls,
        lifecycle_status: str | None,
    ) -> RelationshipLifecycleStatus | None:
        if lifecycle_status is None:
            return lifecycle_status
        return normalize_str_enum_value(
            RelationshipLifecycleStatus,
            lifecycle_status,
        )

    @field_validator("visibility_status", mode="before")
    @classmethod
    def validate_visibility_status(
        cls,
        visibility_status: str | None,
    ) -> RelationshipVisibilityStatus | None:
        if visibility_status is None:
            return visibility_status
        return normalize_str_enum_value(
            RelationshipVisibilityStatus,
            visibility_status,
        )

    @field_validator("certainty_status", mode="before")
    @classmethod
    def validate_certainty_status(
        cls,
        certainty_status: str | None,
    ) -> RelationshipCertaintyStatus | None:
        if certainty_status is None:
            return certainty_status
        return normalize_str_enum_value(
            RelationshipCertaintyStatus,
            certainty_status,
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
    relationship_family: RelationshipFamily
    forward_label: str
    reverse_label: str
    is_symmetric: bool
    lifecycle_status: RelationshipLifecycleStatus
    visibility_status: RelationshipVisibilityStatus
    certainty_status: RelationshipCertaintyStatus
    notes: str | None
    confidence: float | None
    source_document_id: UUID | None
    provenance_excerpt: str | None
    provenance_data: dict[str, object]
    created_at: datetime
    updated_at: datetime

    @field_serializer("relationship_family")
    def serialize_relationship_family(self, relationship_family: RelationshipFamily) -> str:
        return relationship_family.value

    @field_serializer("lifecycle_status", "visibility_status", "certainty_status")
    def serialize_relationship_status(self, status_value) -> str:
        return status_value.value
