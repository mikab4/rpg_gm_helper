from __future__ import annotations

from app.models.campaign import Campaign
from app.models.entity import Entity


def test_entity_type_compatibility_report_groups_legacy_types(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add_all(
            [
                Entity(campaign_id=test_campaign.id, type="npc", name="Rowan"),
                Entity(campaign_id=test_campaign.id, type="npc", name="Mira"),
                Entity(campaign_id=test_campaign.id, type="faction", name="Night Choir"),
                Entity(campaign_id=test_campaign.id, type="location", name="Blackharbor"),
            ]
        )
        db_session.commit()

    response = api_request("GET", "/api/compatibility/entity-types")

    assert response.status_code == 200
    payload = response.json()

    assert payload["has_issues"] is True
    assert payload["issue_count"] == 2
    assert [issue["legacy_type"] for issue in payload["issues"]] == ["faction", "npc"]
    assert payload["issues"][0]["count"] == 1
    assert payload["issues"][0]["example_entities"][0]["entity_name"] == "Night Choir"
    assert payload["issues"][0]["example_entities"][0]["campaign_name"] == "Shadows of Glass"
    assert payload["issues"][1]["count"] == 2
    assert [entity["entity_name"] for entity in payload["issues"][1]["example_entities"]] == [
        "Mira",
        "Rowan",
    ]


def test_entity_type_compatibility_report_returns_clean_state_when_no_issues(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add(Entity(campaign_id=test_campaign.id, type="person", name="Rowan"))
        db_session.commit()

    response = api_request("GET", "/api/compatibility/entity-types")

    assert response.status_code == 200
    assert response.json() == {"has_issues": False, "issue_count": 0, "issues": []}


def test_entity_type_compatibility_migration_applies_explicit_mapping(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add_all(
            [
                Entity(campaign_id=test_campaign.id, type="npc", name="Rowan"),
                Entity(campaign_id=test_campaign.id, type="faction", name="Night Choir"),
            ]
        )
        db_session.commit()

    response = api_request(
        "POST",
        "/api/compatibility/entity-types/migrate",
        json={
            "mappings": [
                {"legacy_type": "npc", "target_type": "person"},
                {"legacy_type": "faction", "target_type": "organization"},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "updated_count": 2,
        "updated_types": [
            {"legacy_type": "faction", "target_type": "organization", "updated_count": 1},
            {"legacy_type": "npc", "target_type": "person", "updated_count": 1},
        ],
    }

    list_response = api_request("GET", "/api/entities")
    assert list_response.status_code == 200
    assert [entity["type"] for entity in list_response.json()] == ["organization", "person"]


def test_entity_type_compatibility_migration_rejects_missing_legacy_mapping(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add_all(
            [
                Entity(campaign_id=test_campaign.id, type="npc", name="Rowan"),
                Entity(campaign_id=test_campaign.id, type="faction", name="Night Choir"),
            ]
        )
        db_session.commit()

    response = api_request(
        "POST",
        "/api/compatibility/entity-types/migrate",
        json={"mappings": [{"legacy_type": "npc", "target_type": "person"}]},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Missing mappings for legacy entity types: faction."}
