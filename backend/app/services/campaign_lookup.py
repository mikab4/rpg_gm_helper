from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Campaign
from app.services.errors import NotFoundError


def get_campaign_or_raise(db_session: Session, campaign_id: UUID) -> Campaign:
    stored_campaign = db_session.get(Campaign, campaign_id)
    if stored_campaign is None:
        raise NotFoundError("Campaign not found.")
    return stored_campaign


def ensure_campaign_exists(db_session: Session, campaign_id: UUID) -> None:
    get_campaign_or_raise(db_session, campaign_id)
