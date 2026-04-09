from __future__ import annotations

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Campaign, Entity, Relationship, SourceDocument
from app.schemas import RelationshipCreate, RelationshipUpdate
from app.services.errors import ConflictError, NotFoundError
from app.services.relationship_catalog import (
    get_relationship_type_descriptor,
    normalize_relationship_type,
)


def create_relationship(
    db_session: Session,
    *,
    campaign_id: UUID,
    relationship_create: RelationshipCreate,
) -> Relationship:
    _ensure_campaign_exists(db_session, campaign_id)
    source_entity = _get_campaign_entity(
        db_session,
        campaign_id=campaign_id,
        entity_id=relationship_create.source_entity_id,
        not_found_message="Source entity not found.",
    )
    target_entity = _get_campaign_entity(
        db_session,
        campaign_id=campaign_id,
        entity_id=relationship_create.target_entity_id,
        not_found_message="Target entity not found.",
    )
    _validate_source_document(
        db_session,
        campaign_id=campaign_id,
        source_document_id=relationship_create.source_document_id,
    )

    relationship_descriptor = _get_descriptor_or_raise(
        db_session,
        campaign_id=campaign_id,
        relationship_type=relationship_create.relationship_type,
    )
    _validate_type_pair(
        source_entity_type=source_entity.type,
        target_entity_type=target_entity.type,
        relationship_descriptor=relationship_descriptor,
    )
    _validate_duplicates(
        db_session,
        campaign_id=campaign_id,
        relationship_type=relationship_descriptor.key,
        source_entity_id=source_entity.id,
        target_entity_id=target_entity.id,
        is_symmetric=relationship_descriptor.is_symmetric,
    )

    created_relationship = Relationship(
        campaign_id=campaign_id,
        source_entity_id=source_entity.id,
        target_entity_id=target_entity.id,
        relationship_type=relationship_descriptor.key,
        lifecycle_status=relationship_create.lifecycle_status,
        visibility_status=relationship_create.visibility_status,
        certainty_status=relationship_create.certainty_status,
        notes=relationship_create.notes,
        confidence=relationship_create.confidence,
        source_document_id=relationship_create.source_document_id,
        provenance_excerpt=relationship_create.provenance_excerpt,
        provenance_data=relationship_create.provenance_data,
    )
    db_session.add(created_relationship)
    db_session.commit()
    db_session.refresh(created_relationship)
    return created_relationship


def list_relationships(
    db_session: Session,
    *,
    campaign_id: UUID,
    relationship_type: str | None = None,
    relationship_family: str | None = None,
) -> list[Relationship]:
    _ensure_campaign_exists(db_session, campaign_id)
    statement = select(Relationship).where(Relationship.campaign_id == campaign_id)
    if relationship_type is not None:
        statement = statement.where(
            Relationship.relationship_type == normalize_relationship_type(relationship_type)
        )

    statement = statement.order_by(Relationship.created_at.desc(), Relationship.id)
    listed_relationships = list(db_session.scalars(statement))
    if relationship_family is None:
        return listed_relationships

    normalized_family = relationship_family.strip().lower()
    return [
        listed_relationship
        for listed_relationship in listed_relationships
        if _get_descriptor_or_raise(
            db_session,
            campaign_id=campaign_id,
            relationship_type=listed_relationship.relationship_type,
        ).family
        == normalized_family
    ]


def get_relationship(
    db_session: Session,
    *,
    campaign_id: UUID,
    relationship_id: UUID,
) -> Relationship:
    stored_relationship = db_session.scalar(
        select(Relationship).where(
            Relationship.id == relationship_id,
            Relationship.campaign_id == campaign_id,
        )
    )
    if stored_relationship is None:
        raise NotFoundError("Relationship not found.")
    return stored_relationship


def update_relationship(
    db_session: Session,
    *,
    campaign_id: UUID,
    relationship_id: UUID,
    relationship_update: RelationshipUpdate,
) -> Relationship:
    stored_relationship = get_relationship(
        db_session,
        campaign_id=campaign_id,
        relationship_id=relationship_id,
    )
    update_fields = relationship_update.model_dump(exclude_unset=True)
    if "source_document_id" in update_fields:
        _validate_source_document(
            db_session,
            campaign_id=campaign_id,
            source_document_id=update_fields["source_document_id"],
        )
    if "relationship_type" in update_fields:
        relationship_descriptor = _get_descriptor_or_raise(
            db_session,
            campaign_id=campaign_id,
            relationship_type=update_fields["relationship_type"],
        )
        source_entity = _get_campaign_entity(
            db_session,
            campaign_id=campaign_id,
            entity_id=stored_relationship.source_entity_id,
            not_found_message="Source entity not found.",
        )
        target_entity = _get_campaign_entity(
            db_session,
            campaign_id=campaign_id,
            entity_id=stored_relationship.target_entity_id,
            not_found_message="Target entity not found.",
        )
        _validate_type_pair(
            source_entity_type=source_entity.type,
            target_entity_type=target_entity.type,
            relationship_descriptor=relationship_descriptor,
        )
        _validate_duplicates(
            db_session,
            campaign_id=campaign_id,
            relationship_type=relationship_descriptor.key,
            source_entity_id=stored_relationship.source_entity_id,
            target_entity_id=stored_relationship.target_entity_id,
            is_symmetric=relationship_descriptor.is_symmetric,
            existing_relationship_id=stored_relationship.id,
        )
        update_fields["relationship_type"] = relationship_descriptor.key

    for field_name, field_value in update_fields.items():
        setattr(stored_relationship, field_name, field_value)

    db_session.commit()
    db_session.refresh(stored_relationship)
    return stored_relationship


def delete_relationship(
    db_session: Session,
    *,
    campaign_id: UUID,
    relationship_id: UUID,
) -> None:
    stored_relationship = get_relationship(
        db_session,
        campaign_id=campaign_id,
        relationship_id=relationship_id,
    )
    db_session.delete(stored_relationship)
    db_session.commit()


def build_relationship_response_payload(
    db_session: Session,
    *,
    relationship: Relationship,
) -> dict[str, object]:
    relationship_descriptor = _get_descriptor_or_raise(
        db_session,
        campaign_id=relationship.campaign_id,
        relationship_type=relationship.relationship_type,
    )
    return {
        "id": relationship.id,
        "campaign_id": relationship.campaign_id,
        "source_entity_id": relationship.source_entity_id,
        "target_entity_id": relationship.target_entity_id,
        "relationship_type": relationship.relationship_type,
        "relationship_family": relationship_descriptor.family,
        "forward_label": relationship_descriptor.label,
        "reverse_label": relationship_descriptor.reverse_label,
        "is_symmetric": relationship_descriptor.is_symmetric,
        "lifecycle_status": relationship.lifecycle_status,
        "visibility_status": relationship.visibility_status,
        "certainty_status": relationship.certainty_status,
        "notes": relationship.notes,
        "confidence": (
            float(relationship.confidence) if relationship.confidence is not None else None
        ),
        "source_document_id": relationship.source_document_id,
        "provenance_excerpt": relationship.provenance_excerpt,
        "provenance_data": relationship.provenance_data,
        "created_at": relationship.created_at,
        "updated_at": relationship.updated_at,
    }


def _ensure_campaign_exists(db_session: Session, campaign_id: UUID) -> None:
    if db_session.get(Campaign, campaign_id) is None:
        raise NotFoundError("Campaign not found.")


def _get_campaign_entity(
    db_session: Session,
    *,
    campaign_id: UUID,
    entity_id: UUID,
    not_found_message: str,
) -> Entity:
    stored_entity = db_session.scalar(
        select(Entity).where(
            Entity.id == entity_id,
            Entity.campaign_id == campaign_id,
        )
    )
    if stored_entity is None:
        raise NotFoundError(not_found_message)
    return stored_entity


def _validate_source_document(
    db_session: Session,
    *,
    campaign_id: UUID,
    source_document_id: UUID | None,
) -> None:
    if source_document_id is None:
        return
    stored_document = db_session.scalar(
        select(SourceDocument.id).where(
            SourceDocument.id == source_document_id,
            SourceDocument.campaign_id == campaign_id,
        )
    )
    if stored_document is None:
        raise NotFoundError("Source document not found.")


def _get_descriptor_or_raise(
    db_session: Session,
    *,
    campaign_id: UUID,
    relationship_type: str,
):
    relationship_descriptor = get_relationship_type_descriptor(
        db_session,
        relationship_type_key=relationship_type,
        campaign_id=campaign_id,
    )
    if relationship_descriptor is None:
        raise NotFoundError("Relationship type not found.")
    return relationship_descriptor


def _validate_type_pair(
    *,
    source_entity_type: str,
    target_entity_type: str,
    relationship_descriptor,
) -> None:
    if source_entity_type not in relationship_descriptor.allowed_source_types:
        raise ValueError("Relationship type is not valid for the source and target entity types.")
    if target_entity_type not in relationship_descriptor.allowed_target_types:
        raise ValueError("Relationship type is not valid for the source and target entity types.")


def _validate_duplicates(
    db_session: Session,
    *,
    campaign_id: UUID,
    relationship_type: str,
    source_entity_id: UUID,
    target_entity_id: UUID,
    is_symmetric: bool,
    existing_relationship_id: UUID | None = None,
) -> None:
    duplicate_conditions = [
        Relationship.campaign_id == campaign_id,
        Relationship.relationship_type == relationship_type,
    ]
    if existing_relationship_id is not None:
        duplicate_conditions.append(Relationship.id != existing_relationship_id)

    if is_symmetric:
        duplicate_statement = select(Relationship.id).where(
            *duplicate_conditions,
            or_(
                (Relationship.source_entity_id == source_entity_id)
                & (Relationship.target_entity_id == target_entity_id),
                (Relationship.source_entity_id == target_entity_id)
                & (Relationship.target_entity_id == source_entity_id),
            ),
        )
        if db_session.scalar(duplicate_statement) is not None:
            raise ConflictError("Symmetric relationship already exists for these entities.")
        return

    duplicate_statement = select(Relationship.id).where(
        *duplicate_conditions,
        Relationship.source_entity_id == source_entity_id,
        Relationship.target_entity_id == target_entity_id,
    )
    if db_session.scalar(duplicate_statement) is not None:
        raise ConflictError("Relationship already exists for these entities.")
