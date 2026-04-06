from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Campaign, Entity
from app.schemas import EntityCreate, EntityUpdate
from app.services.errors import NotFoundError


def create_entity(
    db_session: Session,
    *,
    campaign_id: UUID,
    entity_create: EntityCreate,
) -> Entity:
    if db_session.get(Campaign, campaign_id) is None:
        raise NotFoundError("Campaign not found.")

    created_entity = Entity(
        campaign_id=campaign_id,
        type=entity_create.type,
        name=entity_create.name,
        summary=entity_create.summary,
        metadata_=entity_create.metadata,
    )
    db_session.add(created_entity)
    db_session.commit()
    db_session.refresh(created_entity)
    return created_entity


def list_entities(
    db_session: Session,
    *,
    campaign_id: UUID | None = None,
    entity_type: str | None = None,
) -> list[Entity]:
    statement = select(Entity)
    if campaign_id is not None:
        statement = statement.where(Entity.campaign_id == campaign_id)

    if entity_type is not None:
        statement = statement.where(Entity.type == entity_type)

    statement = statement.order_by(Entity.name.asc(), Entity.id)
    return list(db_session.scalars(statement))


def get_entity(db_session: Session, *, campaign_id: UUID, entity_id: UUID) -> Entity:
    statement = select(Entity).where(
        Entity.id == entity_id,
        Entity.campaign_id == campaign_id,
    )
    stored_entity = db_session.scalar(statement)
    if stored_entity is None:
        raise NotFoundError("Entity not found.")
    return stored_entity


def update_entity(
    db_session: Session,
    *,
    campaign_id: UUID,
    entity_id: UUID,
    entity_update: EntityUpdate,
) -> Entity:
    stored_entity = get_entity(
        db_session,
        campaign_id=campaign_id,
        entity_id=entity_id,
    )
    entity_update_fields = entity_update.model_dump(exclude_unset=True)

    if "metadata" in entity_update_fields:
        stored_entity.metadata_ = entity_update_fields.pop("metadata")

    for field_name, field_value in entity_update_fields.items():
        setattr(stored_entity, field_name, field_value)

    db_session.commit()
    db_session.refresh(stored_entity)
    return stored_entity


def delete_entity(db_session: Session, *, campaign_id: UUID, entity_id: UUID) -> None:
    stored_entity = get_entity(
        db_session,
        campaign_id=campaign_id,
        entity_id=entity_id,
    )
    db_session.delete(stored_entity)
    db_session.commit()
