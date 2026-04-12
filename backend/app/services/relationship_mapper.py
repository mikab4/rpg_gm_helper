from __future__ import annotations

from sqlalchemy.orm import Session

from app.enums import format_relationship_family_label
from app.models import Relationship
from app.services.relationship_catalog import RelationshipTypeDescriptor
from app.services.relationship_descriptor_resolver import (
    build_descriptor_map,
    get_descriptor_or_raise,
)


def build_relationship_response_payload(
    db_session: Session,
    *,
    relationship: Relationship,
) -> dict[str, object]:
    relationship_descriptor = get_descriptor_or_raise(
        db_session,
        campaign_id=relationship.campaign_id,
        relationship_type=relationship.relationship_type,
    )
    return _build_relationship_response_payload_from_descriptor(
        relationship=relationship,
        relationship_descriptor=relationship_descriptor,
    )


def build_relationship_response_payloads(
    db_session: Session,
    *,
    relationships: list[Relationship],
) -> list[dict[str, object]]:
    descriptor_by_type_and_campaign = build_descriptor_map(
        db_session,
        relationships=relationships,
    )
    return [
        _build_relationship_response_payload_from_descriptor(
            relationship=relationship,
            relationship_descriptor=descriptor_by_type_and_campaign[
                (relationship.campaign_id, relationship.relationship_type)
            ],
        )
        for relationship in relationships
    ]


def _build_relationship_response_payload_from_descriptor(
    *,
    relationship: Relationship,
    relationship_descriptor: RelationshipTypeDescriptor,
) -> dict[str, object]:
    return {
        "id": relationship.id,
        "campaign_id": relationship.campaign_id,
        "source_entity_id": relationship.source_entity_id,
        "target_entity_id": relationship.target_entity_id,
        "relationship_type": relationship.relationship_type,
        "relationship_family": relationship_descriptor.family,
        "relationship_family_label": format_relationship_family_label(relationship_descriptor.family),
        "forward_label": relationship_descriptor.label,
        "reverse_label": relationship_descriptor.reverse_label,
        "is_symmetric": relationship_descriptor.is_symmetric,
        "lifecycle_status": relationship.lifecycle_status,
        "visibility_status": relationship.visibility_status,
        "certainty_status": relationship.certainty_status,
        "notes": relationship.notes,
        "confidence": (float(relationship.confidence) if relationship.confidence is not None else None),
        "source_document_id": relationship.source_document_id,
        "provenance_excerpt": relationship.provenance_excerpt,
        "provenance_data": relationship.provenance_data,
        "created_at": relationship.created_at,
        "updated_at": relationship.updated_at,
    }
