from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.routes.campaigns import (
    create_campaign,
    delete_campaign,
    get_campaign,
    list_campaigns,
    update_campaign,
)
from app.models.campaign import Campaign
from app.models.owner import Owner
from app.schemas import CampaignCreate, CampaignUpdate


def test_create_campaign_returns_created_record(db_session: Session, test_owner: Owner) -> None:
    created_campaign_response = create_campaign(
        CampaignCreate(
            owner_id=test_owner.id,
            name="Iron Vale",
            description="Frontier survival",
        ),
        db_session,
    )

    assert created_campaign_response.owner_id == test_owner.id
    assert created_campaign_response.name == "Iron Vale"
    assert created_campaign_response.description == "Frontier survival"


def test_create_campaign_returns_not_found_for_unknown_owner(db_session: Session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        create_campaign(
            CampaignCreate(
                owner_id=uuid4(),
                name="Iron Vale",
            ),
            db_session,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Owner not found."


def test_create_campaign_returns_conflict_for_duplicate_owner_name(
    db_session: Session,
    test_owner: Owner,
) -> None:
    create_campaign(
        CampaignCreate(
            owner_id=test_owner.id,
            name="Iron Vale",
        ),
        db_session,
    )

    with pytest.raises(HTTPException) as exc_info:
        create_campaign(
            CampaignCreate(
                owner_id=test_owner.id,
                name="Iron Vale",
            ),
            db_session,
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Campaign name already exists for this owner."


def test_list_campaigns_supports_owner_filter(db_session: Session, test_owner: Owner) -> None:
    second_owner = Owner(email="other@example.com", display_name="Other GM")
    db_session.add(second_owner)
    db_session.flush()
    db_session.add_all(
        [
            Campaign(owner_id=test_owner.id, name="Iron Vale"),
            Campaign(owner_id=second_owner.id, name="Starfall"),
        ]
    )
    db_session.commit()

    listed_campaigns = list_campaigns(db_session, owner_id=test_owner.id)

    assert [listed_campaign.name for listed_campaign in listed_campaigns] == ["Iron Vale"]


def test_get_update_and_delete_campaign_flow(db_session: Session, test_campaign: Campaign) -> None:
    fetched_campaign_response = get_campaign(test_campaign.id, db_session)

    assert fetched_campaign_response.name == "Shadows of Glass"

    updated_campaign_response = update_campaign(
        test_campaign.id,
        CampaignUpdate(name="Shadows Revised", description="Updated"),
        db_session,
    )

    assert updated_campaign_response.name == "Shadows Revised"
    assert updated_campaign_response.description == "Updated"

    delete_campaign_response = delete_campaign(test_campaign.id, db_session)
    assert delete_campaign_response.status_code == 204

    with pytest.raises(HTTPException) as exc_info:
        get_campaign(test_campaign.id, db_session)

    assert exc_info.value.status_code == 404
