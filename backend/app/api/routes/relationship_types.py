from __future__ import annotations

from datetime import datetime
from typing import Annotated, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.enums import EntityType, RelationshipFamily
from app.schemas import RelationshipTypeCreate, RelationshipTypeResponse, RelationshipTypeUpdate
from app.services import ConflictError, NotFoundError, relationship_type_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db_session)]


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
