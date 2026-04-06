from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import CampaignCreate, CampaignUpdate, EntityCreate, EntityUpdate


def test_campaign_create_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CampaignCreate(
            owner_id=uuid4(),
            name="Iron Vale",
            rogue="x",
        )


def test_entity_create_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        EntityCreate(
            type="npc",
            name="Magistrate Ilya",
            rogue="x",
        )


@pytest.mark.parametrize(
    ("campaign_name", "entity_type", "entity_name"),
    [
        ("", "npc", "Magistrate Ilya"),
        ("   ", "npc", "Magistrate Ilya"),
        ("Iron Vale", "", "Magistrate Ilya"),
        ("Iron Vale", "   ", "Magistrate Ilya"),
        ("Iron Vale", "npc", ""),
        ("Iron Vale", "npc", "   "),
    ],
)
def test_required_business_strings_reject_blank_values(
    campaign_name: str,
    entity_type: str,
    entity_name: str,
) -> None:
    if campaign_name != "Iron Vale":
        with pytest.raises(ValidationError):
            CampaignCreate(owner_id=uuid4(), name=campaign_name)

    if entity_type != "npc" or entity_name != "Magistrate Ilya":
        with pytest.raises(ValidationError):
            EntityCreate(type=entity_type, name=entity_name)


def test_request_models_trim_non_blank_strings() -> None:
    created_campaign = CampaignCreate(
        owner_id=uuid4(),
        name="  Iron Vale  ",
        description="  Frontier survival  ",
    )
    created_entity = EntityCreate(
        type="  npc  ",
        name="  Magistrate Ilya  ",
        summary="  A city official with a hidden agenda.  ",
    )

    assert created_campaign.name == "Iron Vale"
    assert created_campaign.description == "Frontier survival"
    assert created_entity.type == "npc"
    assert created_entity.name == "Magistrate Ilya"
    assert created_entity.summary == "A city official with a hidden agenda."


def test_optional_free_text_fields_reject_blank_strings() -> None:
    with pytest.raises(ValidationError):
        CampaignCreate(
            owner_id=uuid4(),
            name="Iron Vale",
            description="   ",
        )

    with pytest.raises(ValidationError):
        CampaignUpdate(description="   ")

    with pytest.raises(ValidationError):
        EntityCreate(
            type="npc",
            name="Magistrate Ilya",
            summary="   ",
        )

    with pytest.raises(ValidationError):
        EntityUpdate(summary="   ")


def test_optional_free_text_update_fields_allow_null_to_clear() -> None:
    campaign_update = CampaignUpdate(description=None)
    entity_update = EntityUpdate(summary=None)

    assert campaign_update.description is None
    assert entity_update.summary is None


def test_update_models_reject_empty_payloads() -> None:
    with pytest.raises(ValidationError):
        CampaignUpdate()

    with pytest.raises(ValidationError):
        EntityUpdate()
