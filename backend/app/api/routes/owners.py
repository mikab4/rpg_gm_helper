from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas import OwnerResponse
from app.services import owner_service

router = APIRouter(prefix="/owners")

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/default", response_model=OwnerResponse)
def get_default_owner(db_session: DbSession) -> OwnerResponse:
    stored_owner = owner_service.get_default_owner(db_session)
    return OwnerResponse.model_validate(stored_owner)
