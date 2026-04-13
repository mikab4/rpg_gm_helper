from __future__ import annotations

from uuid import UUID

import pytest

from app.services.campaign_lookup import ensure_campaign_exists, get_campaign_or_raise
from app.services.errors import NotFoundError


def test_get_campaign_or_raise_returns_stored_campaign(
    db_session_factory,
    campaign_factory,
) -> None:
    with db_session_factory() as db_session:
        stored_campaign = campaign_factory(db_session=db_session)

        loaded_campaign = get_campaign_or_raise(db_session, stored_campaign.id)

    assert loaded_campaign.id == stored_campaign.id


def test_get_campaign_or_raise_raises_for_missing_campaign(db_session_factory) -> None:
    with db_session_factory() as db_session:
        with pytest.raises(NotFoundError, match="Campaign not found\\."):
            get_campaign_or_raise(db_session, UUID("00000000-0000-0000-0000-000000000000"))


def test_ensure_campaign_exists_raises_for_missing_campaign(db_session_factory) -> None:
    with db_session_factory() as db_session:
        with pytest.raises(NotFoundError, match="Campaign not found\\."):
            ensure_campaign_exists(db_session, UUID("00000000-0000-0000-0000-000000000000"))
