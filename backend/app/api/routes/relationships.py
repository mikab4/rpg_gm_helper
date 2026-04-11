from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas import RelationshipCreate, RelationshipResponse, RelationshipUpdate
from app.services import ConflictError, NotFoundError, relationship_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/campaigns/{campaign_id}/relationships",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_relationship(
    campaign_id: UUID,
    relationship_create: RelationshipCreate,
    db_session: DbSession,
) -> RelationshipResponse:
    try:
        created_relationship = relationship_service.create_relationship(
            db_session,
            campaign_id=campaign_id,
            relationship_create=relationship_create,
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

    return RelationshipResponse.model_validate(
        relationship_service.build_relationship_response_payload(
            db_session,
            relationship=created_relationship,
        )
    )


@router.get("/campaigns/{campaign_id}/relationships", response_model=list[RelationshipResponse])
def list_relationships(
    campaign_id: UUID,
    db_session: DbSession,
    relationship_type: Annotated[str | None, Query(alias="type")] = None,
    relationship_family: Annotated[str | None, Query(alias="family")] = None,
) -> list[RelationshipResponse]:
    try:
        listed_relationships = relationship_service.list_relationships(
            db_session,
            campaign_id=campaign_id,
            relationship_type=relationship_type,
            relationship_family=relationship_family,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return [
        RelationshipResponse.model_validate(
            relationship_service.build_relationship_response_payload(
                db_session,
                relationship=listed_relationship,
            )
        )
        for listed_relationship in listed_relationships
    ]


@router.get(
    "/campaigns/{campaign_id}/relationships/{relationship_id}",
    response_model=RelationshipResponse,
)
def get_relationship(
    campaign_id: UUID,
    relationship_id: UUID,
    db_session: DbSession,
) -> RelationshipResponse:
    try:
        stored_relationship = relationship_service.get_relationship(
            db_session,
            campaign_id=campaign_id,
            relationship_id=relationship_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return RelationshipResponse.model_validate(
        relationship_service.build_relationship_response_payload(
            db_session,
            relationship=stored_relationship,
        )
    )


@router.patch(
    "/campaigns/{campaign_id}/relationships/{relationship_id}",
    response_model=RelationshipResponse,
)
def update_relationship(
    campaign_id: UUID,
    relationship_id: UUID,
    relationship_update: RelationshipUpdate,
    db_session: DbSession,
) -> RelationshipResponse:
    try:
        updated_relationship = relationship_service.update_relationship(
            db_session,
            campaign_id=campaign_id,
            relationship_id=relationship_id,
            relationship_update=relationship_update,
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

    return RelationshipResponse.model_validate(
        relationship_service.build_relationship_response_payload(
            db_session,
            relationship=updated_relationship,
        )
    )


@router.delete(
    "/campaigns/{campaign_id}/relationships/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_relationship(
    campaign_id: UUID,
    relationship_id: UUID,
    db_session: DbSession,
) -> Response:
    try:
        relationship_service.delete_relationship(
            db_session,
            campaign_id=campaign_id,
            relationship_id=relationship_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
