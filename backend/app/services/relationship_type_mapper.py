from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.enums import EntityType, RelationshipFamily
from app.schemas import RelationshipTypeResponse


class RelationshipTypeResponseSource(Protocol):
    id: UUID | None
    campaign_id: UUID | None
    key: str
    label: str
    family: RelationshipFamily | str
    reverse_label: str | None
    is_symmetric: bool
    allowed_source_types: list[EntityType | str] | tuple[EntityType | str, ...]
    allowed_target_types: list[EntityType | str] | tuple[EntityType | str, ...]
    created_at: datetime | None
    updated_at: datetime | None


def build_relationship_type_response(
    relationship_type_source: RelationshipTypeResponseSource,
    *,
    is_custom: bool,
) -> RelationshipTypeResponse:
    return RelationshipTypeResponse.model_validate(
        {
            "id": relationship_type_source.id,
            "campaign_id": relationship_type_source.campaign_id,
            "key": relationship_type_source.key,
            "label": relationship_type_source.label,
            "family": relationship_type_source.family,
            "reverse_label": (
                relationship_type_source.label
                if relationship_type_source.is_symmetric
                else relationship_type_source.reverse_label
            ),
            "is_symmetric": relationship_type_source.is_symmetric,
            "allowed_source_types": list(relationship_type_source.allowed_source_types),
            "allowed_target_types": list(relationship_type_source.allowed_target_types),
            "is_custom": is_custom,
            "created_at": relationship_type_source.created_at,
            "updated_at": relationship_type_source.updated_at,
        }
    )
