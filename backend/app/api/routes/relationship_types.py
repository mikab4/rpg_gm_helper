from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.enums import RelationshipFamily
from app.schemas import (
    RelationshipFamilyOptionResponse,
    RelationshipTypeCreate,
    RelationshipTypeResponse,
    RelationshipTypeUpdate,
)
from app.services import ConflictError, NotFoundError, relationship_type_service
from app.services.relationship_type_mapper import build_relationship_type_response

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/relationship-types", response_model=list[RelationshipTypeResponse])
def list_relationship_types(
    db_session: DbSession,
    campaign_id: UUID | None = None,
) -> list[RelationshipTypeResponse]:
    try:
        listed_relationship_types = relationship_type_service.list_relationship_types(
            db_session,
            campaign_id=campaign_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return [
        build_relationship_type_response(
            listed_relationship_type,
            is_custom=listed_relationship_type.is_custom,
        )
        for listed_relationship_type in listed_relationship_types
    ]


@router.get("/relationship-families", response_model=list[RelationshipFamilyOptionResponse])
def list_relationship_families() -> list[RelationshipFamilyOptionResponse]:
    return [
        RelationshipFamilyOptionResponse.from_relationship_family(relationship_family)
        for relationship_family in RelationshipFamily
    ]


@router.post(
    "/campaigns/{campaign_id}/relationship-types",
    response_model=RelationshipTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_relationship_type(
    campaign_id: UUID,
    relationship_type_create: RelationshipTypeCreate,
    db_session: DbSession,
) -> RelationshipTypeResponse:
    try:
        created_relationship_type = relationship_type_service.create_relationship_type(
            db_session,
            campaign_id=campaign_id,
            relationship_type_create=relationship_type_create,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return build_relationship_type_response(created_relationship_type, is_custom=True)


@router.patch(
    "/campaigns/{campaign_id}/relationship-types/{relationship_type_key}",
    response_model=RelationshipTypeResponse,
)
def update_relationship_type(
    campaign_id: UUID,
    relationship_type_key: str,
    relationship_type_update: RelationshipTypeUpdate,
    db_session: DbSession,
) -> RelationshipTypeResponse:
    try:
        updated_relationship_type = relationship_type_service.update_relationship_type(
            db_session,
            campaign_id=campaign_id,
            relationship_type_key=relationship_type_key,
            relationship_type_update=relationship_type_update,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return build_relationship_type_response(updated_relationship_type, is_custom=True)


@router.delete(
    "/campaigns/{campaign_id}/relationship-types/{relationship_type_key}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_relationship_type(
    campaign_id: UUID,
    relationship_type_key: str,
    db_session: DbSession,
) -> Response:
    try:
        relationship_type_service.delete_relationship_type(
            db_session,
            campaign_id=campaign_id,
            relationship_type_key=relationship_type_key,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
