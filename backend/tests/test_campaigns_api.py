from __future__ import annotations

from uuid import uuid4


def test_create_campaign_returns_created_record(
    api_request,
    owner_factory,
) -> None:
    owner = owner_factory()

    response = api_request(
        "POST",
        "/api/campaigns",
        json={
            "owner_id": str(owner.id),
            "name": "Iron Vale",
            "description": "Frontier survival",
        },
    )

    assert response.status_code == 201
    campaign_data = response.json()
    assert campaign_data["owner_id"] == str(owner.id)
    assert campaign_data["name"] == "Iron Vale"
    assert campaign_data["description"] == "Frontier survival"


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
    owner_factory,
    campaign_factory,
) -> None:
    owner = owner_factory()
    campaign_factory(owner=owner, name="Iron Vale")

    response = api_request(
        "POST",
        "/api/campaigns",
        json={
            "owner_id": str(owner.id),
            "name": "Iron Vale",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Campaign name already exists for this owner."}


def test_create_campaign_returns_422_for_unknown_field(
    api_request,
    owner_factory,
) -> None:
    owner = owner_factory()

    response = api_request(
        "POST",
        "/api/campaigns",
        json={
            "owner_id": str(owner.id),
            "name": "Iron Vale",
            "rogue": "x",
        },
    )

    assert response.status_code == 422
    campaign_data = response.json()
    assert campaign_data["detail"][0]["loc"] == ["body", "rogue"]
    assert campaign_data["detail"][0]["type"] == "extra_forbidden"


def test_list_campaigns_supports_owner_filter(
    api_request,
    owner_factory,
    campaign_factory,
) -> None:
    owner = owner_factory(email="gm@example.com", display_name="Local GM")
    second_owner = owner_factory(email="other@example.com", display_name="Other GM")
    campaign_factory(owner=owner, name="Iron Vale")
    campaign_factory(owner=second_owner, name="Starfall")

    response = api_request("GET", "/api/campaigns", params={"owner_id": str(owner.id)})

    assert response.status_code == 200
    assert [listed_campaign["name"] for listed_campaign in response.json()] == ["Iron Vale"]


def test_get_campaign_returns_stored_record(
    api_request,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory(name="Shadows of Glass")

    response = api_request("GET", f"/api/campaigns/{stored_campaign.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Shadows of Glass"


def test_update_campaign_returns_updated_fields(
    api_request,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory(name="Shadows of Glass")

    response = api_request(
        "PATCH",
        f"/api/campaigns/{stored_campaign.id}",
        json={
            "name": "Shadows Revised",
            "description": "Updated",
        },
    )

    assert response.status_code == 200
    campaign_data = response.json()
    assert campaign_data["name"] == "Shadows Revised"
    assert campaign_data["description"] == "Updated"


def test_delete_campaign_removes_campaign(
    api_request,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory()

    delete_response = api_request("DELETE", f"/api/campaigns/{stored_campaign.id}")

    assert delete_response.status_code == 204

    missing_response = api_request("GET", f"/api/campaigns/{stored_campaign.id}")
    assert missing_response.status_code == 404


def test_delete_campaign_succeeds_when_campaign_has_entities(
    api_request,
    campaign_factory,
    entity_factory,
) -> None:
    stored_campaign = campaign_factory()
    entity_factory(
        campaign_id=stored_campaign.id,
        type="npc",
        name="Zam the man",
        summary="Head of wappana",
    )

    delete_response = api_request("DELETE", f"/api/campaigns/{stored_campaign.id}")

    assert delete_response.status_code == 204

    missing_response = api_request("GET", f"/api/campaigns/{stored_campaign.id}")
    assert missing_response.status_code == 404


def test_update_campaign_returns_422_for_null_name(
    api_request,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory()

    response = api_request(
        "PATCH",
        f"/api/campaigns/{stored_campaign.id}",
        json={
            "name": None,
            "description": "Updated",
        },
    )

    assert response.status_code == 422
    campaign_data = response.json()
    assert campaign_data["detail"][0]["loc"] == ["body"]
    assert campaign_data["detail"][0]["type"] == "value_error"
