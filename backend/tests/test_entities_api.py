from __future__ import annotations

from uuid import uuid4

from app.models.campaign import Campaign
from app.models.entity import Entity


def test_create_entity_returns_created_record(
    api_request,
    test_campaign: Campaign,
) -> None:
    response = api_request(
        "POST",
        f"/api/campaigns/{test_campaign.id}/entities",
        json={
            "type": "npc",
            "name": "Magistrate Ilya",
            "summary": "A city official with a hidden agenda.",
            "metadata": {"faction": "City Watch"},
        },
    )

    assert response.status_code == 201
    assert response.json()["campaign_id"] == str(test_campaign.id)
    assert response.json()["type"] == "npc"
    assert response.json()["name"] == "Magistrate Ilya"
    assert response.json()["metadata"] == {"faction": "City Watch"}


def test_create_entity_returns_not_found_for_unknown_campaign(api_request) -> None:
    response = api_request(
        "POST",
        f"/api/campaigns/{uuid4()}/entities",
        json={
            "type": "npc",
            "name": "Magistrate Ilya",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Campaign not found."}


def test_create_entity_returns_422_for_blank_name(
    api_request,
    test_campaign: Campaign,
) -> None:
    response = api_request(
        "POST",
        f"/api/campaigns/{test_campaign.id}/entities",
        json={
            "type": "npc",
            "name": "   ",
        },
    )

    assert response.status_code == 422


def test_list_all_entities_returns_cross_campaign_results(
    api_request,
    db_session_factory,
    test_owner,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        second_campaign = Campaign(owner_id=test_owner.id, name="Second Campaign")
        db_session.add(second_campaign)
        db_session.flush()

        db_session.add_all(
            [
                Entity(campaign_id=test_campaign.id, type="npc", name="Magistrate Ilya"),
                Entity(campaign_id=second_campaign.id, type="faction", name="Varkesh"),
            ]
        )
        db_session.commit()

    response = api_request("GET", "/api/entities")

    assert response.status_code == 200
    assert [listed_entity["name"] for listed_entity in response.json()] == [
        "Magistrate Ilya",
        "Varkesh",
    ]


def test_list_all_entities_supports_campaign_and_type_filters(
    api_request,
    db_session_factory,
    test_owner,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        second_campaign = Campaign(owner_id=test_owner.id, name="Second Campaign")
        db_session.add(second_campaign)
        db_session.flush()

        db_session.add_all(
            [
                Entity(campaign_id=test_campaign.id, type="npc", name="Magistrate Ilya"),
                Entity(campaign_id=test_campaign.id, type="location", name="Broken Observatory"),
                Entity(campaign_id=second_campaign.id, type="npc", name="Varkesh"),
            ]
        )
        db_session.commit()

    response = api_request(
        "GET",
        "/api/entities",
        params={
            "campaign_id": str(test_campaign.id),
            "type": "npc",
        },
    )

    assert response.status_code == 200
    assert [listed_entity["name"] for listed_entity in response.json()] == ["Magistrate Ilya"]


def test_list_campaign_entities_supports_type_filter(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add_all(
            [
                Entity(campaign_id=test_campaign.id, type="npc", name="Magistrate Ilya"),
                Entity(campaign_id=test_campaign.id, type="location", name="Broken Observatory"),
            ]
        )
        db_session.commit()

    response = api_request(
        "GET",
        f"/api/campaigns/{test_campaign.id}/entities",
        params={"type": "npc"},
    )

    assert response.status_code == 200
    assert [listed_entity["name"] for listed_entity in response.json()] == ["Magistrate Ilya"]


def test_get_update_and_delete_entity_flow(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        stored_entity = Entity(
            campaign_id=test_campaign.id,
            type="npc",
            name="Magistrate Ilya",
            summary="Before update",
        )
        db_session.add(stored_entity)
        db_session.commit()
        db_session.refresh(stored_entity)
        stored_entity_id = stored_entity.id

    get_response = api_request(
        "GET",
        f"/api/campaigns/{test_campaign.id}/entities/{stored_entity_id}",
    )

    assert get_response.status_code == 200
    assert get_response.json()["summary"] == "Before update"

    update_response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}/entities/{stored_entity_id}",
        json={
            "type": "faction",
            "name": "Ilya",
            "summary": "After update",
            "metadata": {"rank": "magistrate"},
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["type"] == "faction"
    assert update_response.json()["name"] == "Ilya"
    assert update_response.json()["summary"] == "After update"
    assert update_response.json()["metadata"] == {"rank": "magistrate"}

    delete_response = api_request(
        "DELETE",
        f"/api/campaigns/{test_campaign.id}/entities/{stored_entity_id}",
    )
    assert delete_response.status_code == 204

    missing_response = api_request(
        "GET",
        f"/api/campaigns/{test_campaign.id}/entities/{stored_entity_id}",
    )
    assert missing_response.status_code == 404


def test_get_entity_returns_not_found_for_campaign_mismatch(
    api_request,
    db_session_factory,
    test_owner,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        second_campaign = Campaign(owner_id=test_owner.id, name="Second Campaign")
        db_session.add(second_campaign)
        db_session.flush()

        stored_entity = Entity(
            campaign_id=test_campaign.id,
            type="npc",
            name="Magistrate Ilya",
        )
        db_session.add(stored_entity)
        db_session.commit()
        db_session.refresh(stored_entity)
        second_campaign_id = second_campaign.id
        stored_entity_id = stored_entity.id

    response = api_request(
        "GET",
        f"/api/campaigns/{second_campaign_id}/entities/{stored_entity_id}",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Entity not found."}


def test_update_entity_returns_422_for_null_name(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        stored_entity = Entity(
            campaign_id=test_campaign.id,
            type="npc",
            name="Magistrate Ilya",
        )
        db_session.add(stored_entity)
        db_session.commit()
        db_session.refresh(stored_entity)
        stored_entity_id = stored_entity.id

    response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}/entities/{stored_entity_id}",
        json={
            "name": None,
            "summary": "Updated",
        },
    )

    assert response.status_code == 422
