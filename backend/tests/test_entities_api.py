from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.routes.entities import (
    create_entity,
    delete_entity,
    get_entity,
    list_entities,
    update_entity,
)
from app.models.campaign import Campaign
from app.models.entity import Entity
from app.schemas import EntityCreate, EntityUpdate


def test_create_entity_returns_created_record(db_session: Session, test_campaign: Campaign) -> None:
    created_entity_response = create_entity(
        EntityCreate(
            campaign_id=test_campaign.id,
            type="npc",
            name="Magistrate Ilya",
            summary="A city official with a hidden agenda.",
            metadata={"faction": "City Watch"},
        ),
        db_session,
    )

    assert created_entity_response.campaign_id == test_campaign.id
    assert created_entity_response.type == "npc"
    assert created_entity_response.name == "Magistrate Ilya"
    assert created_entity_response.metadata == {"faction": "City Watch"}


def test_create_entity_returns_not_found_for_unknown_campaign(db_session: Session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        create_entity(
            EntityCreate(
                campaign_id=uuid4(),
                type="npc",
                name="Magistrate Ilya",
            ),
            db_session,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Campaign not found."


def test_list_entities_supports_type_filter(db_session: Session, test_campaign: Campaign) -> None:
    db_session.add_all(
        [
            Entity(campaign_id=test_campaign.id, type="npc", name="Magistrate Ilya"),
            Entity(campaign_id=test_campaign.id, type="location", name="Broken Observatory"),
        ]
    )
    db_session.commit()

    listed_entities = list_entities(db_session, campaign_id=test_campaign.id, type="npc")

    assert [listed_entity.name for listed_entity in listed_entities] == ["Magistrate Ilya"]


def test_get_update_and_delete_entity_flow(db_session: Session, test_campaign: Campaign) -> None:
    stored_entity = Entity(
        campaign_id=test_campaign.id,
        type="npc",
        name="Magistrate Ilya",
        summary="Before update",
    )
    db_session.add(stored_entity)
    db_session.commit()
    db_session.refresh(stored_entity)

    fetched_entity_response = get_entity(stored_entity.id, db_session)

    assert fetched_entity_response.summary == "Before update"

    updated_entity_response = update_entity(
        stored_entity.id,
        EntityUpdate(
            type="ally",
            name="Ilya",
            summary="After update",
            metadata={"rank": "magistrate"},
        ),
        db_session,
    )

    assert updated_entity_response.type == "ally"
    assert updated_entity_response.name == "Ilya"
    assert updated_entity_response.summary == "After update"
    assert updated_entity_response.metadata == {"rank": "magistrate"}

    delete_entity_response = delete_entity(stored_entity.id, db_session)
    assert delete_entity_response.status_code == 204

    with pytest.raises(HTTPException) as exc_info:
        get_entity(stored_entity.id, db_session)

    assert exc_info.value.status_code == 404
