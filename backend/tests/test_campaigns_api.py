from __future__ import annotations

from uuid import uuid4

from app.models.campaign import Campaign
from app.models.entity import Entity
from app.models.owner import Owner


def test_create_campaign_returns_created_record(
    api_request,
    test_owner: Owner,
) -> None:
    response = api_request(
        "POST",
        "/api/campaigns",
        json={
            "owner_id": str(test_owner.id),
            "name": "Iron Vale",
            "description": "Frontier survival",
        },
    )

    assert response.status_code == 201
    assert response.json()["owner_id"] == str(test_owner.id)
    assert response.json()["name"] == "Iron Vale"
    assert response.json()["description"] == "Frontier survival"


def test_create_campaign_returns_not_found_for_unknown_owner(api_request) -> None:
    response = api_request(
        "POST",
        "/api/campaigns",
        json={
            "owner_id": str(uuid4()),
            "name": "Iron Vale",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Owner not found."}


def test_create_campaign_returns_conflict_for_duplicate_owner_name(
    api_request,
    test_owner: Owner,
) -> None:
    api_request(
        "POST",
        "/api/campaigns",
        json={
            "owner_id": str(test_owner.id),
            "name": "Iron Vale",
        },
    )

    response = api_request(
        "POST",
        "/api/campaigns",
        json={
            "owner_id": str(test_owner.id),
            "name": "Iron Vale",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Campaign name already exists for this owner."}


def test_create_campaign_returns_422_for_unknown_field(
    api_request,
    test_owner: Owner,
) -> None:
    response = api_request(
        "POST",
        "/api/campaigns",
        json={
            "owner_id": str(test_owner.id),
            "name": "Iron Vale",
            "rogue": "x",
        },
    )

    assert response.status_code == 422


def test_list_campaigns_supports_owner_filter(
    api_request,
    db_session_factory,
    test_owner: Owner,
) -> None:
    with db_session_factory() as db_session:
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

    response = api_request("GET", "/api/campaigns", params={"owner_id": str(test_owner.id)})

    assert response.status_code == 200
    assert [listed_campaign["name"] for listed_campaign in response.json()] == ["Iron Vale"]


def test_get_campaign_returns_stored_record(
    api_request,
    test_campaign: Campaign,
) -> None:
    response = api_request("GET", f"/api/campaigns/{test_campaign.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Shadows of Glass"


def test_update_campaign_returns_updated_fields(
    api_request,
    test_campaign: Campaign,
) -> None:
    response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}",
        json={
            "name": "Shadows Revised",
            "description": "Updated",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Shadows Revised"
    assert response.json()["description"] == "Updated"


def test_delete_campaign_removes_campaign(
    api_request,
    test_campaign: Campaign,
) -> None:
    delete_response = api_request("DELETE", f"/api/campaigns/{test_campaign.id}")

    assert delete_response.status_code == 204

    missing_response = api_request("GET", f"/api/campaigns/{test_campaign.id}")
    assert missing_response.status_code == 404


def test_delete_campaign_succeeds_when_campaign_has_entities(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add(
            Entity(
                campaign_id=test_campaign.id,
                type="npc",
                name="Zam the man",
                summary="Head of wappana",
            )
        )
        db_session.commit()

    delete_response = api_request("DELETE", f"/api/campaigns/{test_campaign.id}")

    assert delete_response.status_code == 204

    missing_response = api_request("GET", f"/api/campaigns/{test_campaign.id}")
    assert missing_response.status_code == 404


def test_update_campaign_returns_422_for_null_name(
    api_request,
    test_campaign: Campaign,
) -> None:
    response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}",
        json={
            "name": None,
            "description": "Updated",
        },
    )

    assert response.status_code == 422
