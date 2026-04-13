from __future__ import annotations


def test_entity_type_compatibility_report_groups_legacy_types(
    api_request,
    entity_factory,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory(name="Shadows of Glass")
    entity_factory(campaign_id=stored_campaign.id, type="npc", name="Rowan")
    entity_factory(campaign_id=stored_campaign.id, type="npc", name="Mira")
    entity_factory(campaign_id=stored_campaign.id, type="faction", name="Night Choir")
    entity_factory(campaign_id=stored_campaign.id, type="location", name="Blackharbor")

    response = api_request("GET", "/api/compatibility/entity-types")

    assert response.status_code == 200
    compatibility_report = response.json()

    assert compatibility_report["has_issues"] is True
    assert compatibility_report["issue_count"] == 2
    assert [issue["legacy_type"] for issue in compatibility_report["issues"]] == [
        "faction",
        "npc",
    ]
    assert compatibility_report["issues"][0]["count"] == 1
    assert compatibility_report["issues"][0]["raw_variants"] == ["faction"]
    assert compatibility_report["issues"][0]["example_entities"][0]["entity_name"] == "Night Choir"
    assert (
        compatibility_report["issues"][0]["example_entities"][0]["campaign_name"]
        == "Shadows of Glass"
    )
    assert compatibility_report["issues"][1]["count"] == 2
    assert compatibility_report["issues"][1]["raw_variants"] == ["npc"]
    assert [
        entity["entity_name"]
        for entity in compatibility_report["issues"][1]["example_entities"]
    ] == [
        "Mira",
        "Rowan",
    ]


def test_entity_type_compatibility_report_merges_case_and_whitespace_variants(
    api_request,
    entity_factory,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory()
    entity_factory(campaign_id=stored_campaign.id, type="NPC", name="Rowan")
    entity_factory(campaign_id=stored_campaign.id, type=" npc ", name="Mira")
    entity_factory(campaign_id=stored_campaign.id, type="person", name="Ilya")

    response = api_request("GET", "/api/compatibility/entity-types")

    assert response.status_code == 200
    compatibility_report = response.json()

    assert compatibility_report["has_issues"] is True
    assert compatibility_report["issue_count"] == 1
    assert len(compatibility_report["issues"]) == 1
    assert compatibility_report["issues"][0]["legacy_type"] == "npc"
    assert compatibility_report["issues"][0]["raw_variants"] == [" npc ", "NPC"]
    assert compatibility_report["issues"][0]["count"] == 2
    assert [
        entity["entity_name"]
        for entity in compatibility_report["issues"][0]["example_entities"]
    ] == ["Mira", "Rowan"]


def test_entity_type_compatibility_report_returns_clean_state_when_no_issues(
    api_request,
    entity_factory,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory()
    entity_factory(campaign_id=stored_campaign.id, type="person", name="Rowan")

    response = api_request("GET", "/api/compatibility/entity-types")

    assert response.status_code == 200
    assert response.json() == {"has_issues": False, "issue_count": 0, "issues": []}


def test_entity_type_compatibility_migration_applies_explicit_mapping(
    api_request,
    entity_factory,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory()
    entity_factory(campaign_id=stored_campaign.id, type="npc", name="Rowan")
    entity_factory(campaign_id=stored_campaign.id, type="faction", name="Night Choir")

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
    entity_factory,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory()
    entity_factory(campaign_id=stored_campaign.id, type="npc", name="Rowan")
    entity_factory(campaign_id=stored_campaign.id, type="faction", name="Night Choir")

    response = api_request(
        "POST",
        "/api/compatibility/entity-types/migrate",
        json={"mappings": [{"legacy_type": "npc", "target_type": "person"}]},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Missing mappings for legacy entity types: faction."}


def test_entity_type_compatibility_migration_applies_mapping_to_all_normalized_variants(
    api_request,
    entity_factory,
    campaign_factory,
) -> None:
    stored_campaign = campaign_factory()
    entity_factory(campaign_id=stored_campaign.id, type="NPC", name="Rowan")
    entity_factory(campaign_id=stored_campaign.id, type=" npc ", name="Mira")

    response = api_request(
        "POST",
        "/api/compatibility/entity-types/migrate",
        json={"mappings": [{"legacy_type": "npc", "target_type": "person"}]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "updated_count": 2,
        "updated_types": [
            {"legacy_type": "npc", "target_type": "person", "updated_count": 2},
        ],
    }

    list_response = api_request("GET", "/api/entities")
    assert list_response.status_code == 200
    assert [entity["type"] for entity in list_response.json()] == ["person", "person"]
