from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Owner

DEFAULT_OWNER_EMAIL = "gm@example.com"
DEFAULT_OWNER_DISPLAY_NAME = "Local GM"


def get_default_owner(db_session: Session) -> Owner:
    stored_owner = db_session.scalar(select(Owner).order_by(Owner.created_at, Owner.id))
    if stored_owner is not None:
        return stored_owner

    created_owner = Owner(
        email=DEFAULT_OWNER_EMAIL,
        display_name=DEFAULT_OWNER_DISPLAY_NAME,
    )
    db_session.add(created_owner)
    db_session.commit()
    db_session.refresh(created_owner)
    return created_owner
