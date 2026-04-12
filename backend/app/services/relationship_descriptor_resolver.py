from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Relationship
from app.services.errors import NotFoundError
from app.services.relationship_catalog import (
    RelationshipTypeDescriptor,
    get_relationship_type_descriptor,
)


def get_descriptor_or_raise(
    db_session: Session,
    *,
    campaign_id: UUID,
    relationship_type: str,
) -> RelationshipTypeDescriptor:
    relationship_descriptor = get_relationship_type_descriptor(
        db_session,
        relationship_type_key=relationship_type,
        campaign_id=campaign_id,
    )
    if relationship_descriptor is None:
        raise NotFoundError("Relationship type not found.")
    return relationship_descriptor


def build_descriptor_map(
    db_session: Session,
    *,
    relationships: list[Relationship],
) -> dict[tuple[UUID, str], RelationshipTypeDescriptor]:
    descriptor_by_type_and_campaign: dict[tuple[UUID, str], RelationshipTypeDescriptor] = {}
    for relationship in relationships:
        descriptor_key = (relationship.campaign_id, relationship.relationship_type)
        if descriptor_key in descriptor_by_type_and_campaign:
            continue
        descriptor_by_type_and_campaign[descriptor_key] = get_descriptor_or_raise(
            db_session,
            campaign_id=relationship.campaign_id,
            relationship_type=relationship.relationship_type,
        )
    return descriptor_by_type_and_campaign
