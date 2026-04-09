from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas import (
    RelationshipCreate,
    RelationshipResponse,
    RelationshipTypeCreate,
    RelationshipTypeResponse,
    RelationshipTypeUpdate,
    RelationshipUpdate,
)
from app.services import (
    ConflictError,
    NotFoundError,
    relationship_service,
    relationship_type_service,
)

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
        RelationshipTypeResponse.model_validate(
            {
                "id": listed_relationship_type.id,
                "campaign_id": listed_relationship_type.campaign_id,
                "key": listed_relationship_type.key,
                "label": listed_relationship_type.label,
                "family": listed_relationship_type.family,
                "reverse_label": (
                    listed_relationship_type.label
                    if listed_relationship_type.is_symmetric
                    else listed_relationship_type.reverse_label
                ),
                "is_symmetric": listed_relationship_type.is_symmetric,
                "allowed_source_types": list(listed_relationship_type.allowed_source_types),
                "allowed_target_types": list(listed_relationship_type.allowed_target_types),
                "is_custom": listed_relationship_type.is_custom,
                "created_at": listed_relationship_type.created_at,
                "updated_at": listed_relationship_type.updated_at,
            }
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

    return RelationshipTypeResponse.model_validate(
        {
            "id": created_relationship_type.id,
            "campaign_id": created_relationship_type.campaign_id,
            "key": created_relationship_type.key,
            "label": created_relationship_type.label,
            "family": created_relationship_type.family,
            "reverse_label": (
                created_relationship_type.label
                if created_relationship_type.is_symmetric
                else created_relationship_type.reverse_label
            ),
            "is_symmetric": created_relationship_type.is_symmetric,
            "allowed_source_types": created_relationship_type.allowed_source_types,
            "allowed_target_types": created_relationship_type.allowed_target_types,
            "is_custom": True,
            "created_at": created_relationship_type.created_at,
            "updated_at": created_relationship_type.updated_at,
        }
    )


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

    return RelationshipTypeResponse.model_validate(
        {
            "id": updated_relationship_type.id,
            "campaign_id": updated_relationship_type.campaign_id,
            "key": updated_relationship_type.key,
            "label": updated_relationship_type.label,
            "family": updated_relationship_type.family,
            "reverse_label": (
                updated_relationship_type.label
                if updated_relationship_type.is_symmetric
                else updated_relationship_type.reverse_label
            ),
            "is_symmetric": updated_relationship_type.is_symmetric,
            "allowed_source_types": updated_relationship_type.allowed_source_types,
            "allowed_target_types": updated_relationship_type.allowed_target_types,
            "is_custom": True,
            "created_at": updated_relationship_type.created_at,
            "updated_at": updated_relationship_type.updated_at,
        }
    )


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
