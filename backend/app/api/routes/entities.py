from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas import EntityCreate, EntityResponse, EntityUpdate
from app.services import NotFoundError, entity_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/entities", response_model=list[EntityResponse])
def list_all_entities(
    db_session: DbSession,
    campaign_id: UUID | None = None,
    entity_type: Annotated[str | None, Query(alias="type")] = None,
) -> list[EntityResponse]:
    listed_entities = entity_service.list_entities(
        db_session,
        campaign_id=campaign_id,
        entity_type=entity_type,
    )
    return [EntityResponse.model_validate(listed_entity) for listed_entity in listed_entities]


@router.post(
    "/campaigns/{campaign_id}/entities",
    response_model=EntityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_entity(
    campaign_id: UUID,
    entity_create: EntityCreate,
    db_session: DbSession,
) -> EntityResponse:
    try:
        created_entity = entity_service.create_entity(
            db_session,
            campaign_id=campaign_id,
            entity_create=entity_create,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return EntityResponse.model_validate(created_entity)


@router.get("/campaigns/{campaign_id}/entities", response_model=list[EntityResponse])
def list_campaign_entities(
    campaign_id: UUID,
    db_session: DbSession,
    entity_type: Annotated[str | None, Query(alias="type")] = None,
) -> list[EntityResponse]:
    listed_entities = entity_service.list_entities(
        db_session,
        campaign_id=campaign_id,
        entity_type=entity_type,
    )
    return [EntityResponse.model_validate(listed_entity) for listed_entity in listed_entities]


@router.get("/campaigns/{campaign_id}/entities/{entity_id}", response_model=EntityResponse)
def get_entity(campaign_id: UUID, entity_id: UUID, db_session: DbSession) -> EntityResponse:
    try:
        stored_entity = entity_service.get_entity(
            db_session,
            campaign_id=campaign_id,
            entity_id=entity_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return EntityResponse.model_validate(stored_entity)


@router.patch("/campaigns/{campaign_id}/entities/{entity_id}", response_model=EntityResponse)
def update_entity(
    campaign_id: UUID,
    entity_id: UUID,
    entity_update: EntityUpdate,
    db_session: DbSession,
) -> EntityResponse:
    try:
        updated_entity = entity_service.update_entity(
            db_session,
            campaign_id=campaign_id,
            entity_id=entity_id,
            entity_update=entity_update,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return EntityResponse.model_validate(updated_entity)


@router.delete(
    "/campaigns/{campaign_id}/entities/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_entity(campaign_id: UUID, entity_id: UUID, db_session: DbSession) -> Response:
    try:
        entity_service.delete_entity(
            db_session,
            campaign_id=campaign_id,
            entity_id=entity_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
