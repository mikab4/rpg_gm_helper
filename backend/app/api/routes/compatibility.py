from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.compatibility import (
    EntityTypeCompatibilityReport,
    EntityTypeMigrationRequest,
    EntityTypeMigrationResult,
)
from app.services import ConflictError
from app.services.compatibility_service import (
    build_entity_type_compatibility_report,
    migrate_entity_types,
)

router = APIRouter(prefix="/compatibility")

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/entity-types", response_model=EntityTypeCompatibilityReport)
def get_entity_type_compatibility_report(db_session: DbSession) -> EntityTypeCompatibilityReport:
    return build_entity_type_compatibility_report(db_session)


@router.post("/entity-types/migrate", response_model=EntityTypeMigrationResult)
def apply_entity_type_migration(
    migration_request: EntityTypeMigrationRequest,
    db_session: DbSession,
) -> EntityTypeMigrationResult:
    try:
        return migrate_entity_types(db_session, migration_request)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
