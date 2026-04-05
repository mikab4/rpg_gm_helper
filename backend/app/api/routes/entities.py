from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas import EntityCreate, EntityResponse, EntityUpdate
from app.services import NotFoundError, entity_service

router = APIRouter(prefix="/entities")

DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(entity_create: EntityCreate, db_session: DbSession) -> EntityResponse:
    try:
        created_entity = entity_service.create_entity(db_session, entity_create)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return EntityResponse.model_validate(created_entity)


@router.get("", response_model=list[EntityResponse])
def list_entities(
    db_session: DbSession,
    campaign_id: Annotated[UUID, Query()],
    type: str | None = None,
) -> list[EntityResponse]:
    listed_entities = entity_service.list_entities(
        db_session,
        campaign_id=campaign_id,
        entity_type=type,
    )
    return [EntityResponse.model_validate(listed_entity) for listed_entity in listed_entities]


@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: UUID, db_session: DbSession) -> EntityResponse:
    try:
        stored_entity = entity_service.get_entity(db_session, entity_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return EntityResponse.model_validate(stored_entity)


@router.patch("/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: UUID,
    entity_update: EntityUpdate,
    db_session: DbSession,
) -> EntityResponse:
    try:
        updated_entity = entity_service.update_entity(db_session, entity_id, entity_update)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return EntityResponse.model_validate(updated_entity)


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(entity_id: UUID, db_session: DbSession) -> Response:
    try:
        entity_service.delete_entity(db_session, entity_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
