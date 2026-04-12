from __future__ import annotations

from uuid import uuid4

from app import services
from app.models.campaign import Campaign
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.relationship_type_definition import RelationshipTypeDefinition


def test_list_relationship_types_includes_built_in_and_custom_types(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add(
            RelationshipTypeDefinition(
                id=uuid4(),
                campaign_id=test_campaign.id,
                key="bodyguard_of",
                label="bodyguard of",
                family="social",
                reverse_label="guarded by",
                is_symmetric=False,
                allowed_source_types=["person"],
                allowed_target_types=["person"],
            )
        )
        db_session.commit()

    response = api_request(
        "GET",
        "/api/relationship-types",
        params={"campaign_id": str(test_campaign.id)},
    )

    assert response.status_code == 200
    listed_type_keys = {listed_type["key"] for listed_type in response.json()}
    assert "sibling_of" in listed_type_keys
    assert "bodyguard_of" in listed_type_keys


def test_create_custom_relationship_type_returns_created_record(
    api_request,
    test_campaign: Campaign,
) -> None:
    response = api_request(
        "POST",
        f"/api/campaigns/{test_campaign.id}/relationship-types",
        json={
            "label": "bodyguard of",
            "family": "social",
            "reverse_label": "guarded by",
            "is_symmetric": False,
            "allowed_source_types": ["person"],
            "allowed_target_types": ["person"],
        },
    )

    assert response.status_code == 201
    assert response.json()["key"] == "bodyguard_of"
    assert response.json()["label"] == "bodyguard of"
    assert response.json()["family"] == "social"
    assert response.json()["is_custom"] is True


def test_update_custom_relationship_type_rejects_semantic_changes_when_type_is_in_use(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        entity_a = Entity(campaign_id=test_campaign.id, type="person", name="Martha")
        entity_b = Entity(campaign_id=test_campaign.id, type="person", name="Rick")
        db_session.add_all([entity_a, entity_b])
        db_session.flush()
        db_session.add(
            RelationshipTypeDefinition(
                id=uuid4(),
                campaign_id=test_campaign.id,
                key="bodyguard_of",
                label="bodyguard of",
                family="social",
                reverse_label="guarded by",
                is_symmetric=False,
                allowed_source_types=["person"],
                allowed_target_types=["person"],
            )
        )
        db_session.add(
            Relationship(
                campaign_id=test_campaign.id,
                source_entity=entity_a,
                target_entity=entity_b,
                relationship_type="bodyguard_of",
                lifecycle_status="current",
                visibility_status="public",
                certainty_status="confirmed",
            )
        )
        db_session.commit()

    response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}/relationship-types/bodyguard_of",
        json={"allowed_target_types": ["organization"]},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Semantic fields cannot change after a type is in use."}


def test_update_custom_relationship_type_rejects_payload_with_symmetric_and_reverse_label(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add(
            RelationshipTypeDefinition(
                id=uuid4(),
                campaign_id=test_campaign.id,
                key="bodyguard_of",
                label="bodyguard of",
                family="social",
                reverse_label="guarded by",
                is_symmetric=False,
                allowed_source_types=["person"],
                allowed_target_types=["person"],
            )
        )
        db_session.commit()

    response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}/relationship-types/bodyguard_of",
        json={"is_symmetric": True, "reverse_label": "guarded by"},
    )

    assert response.status_code == 422


def test_update_custom_relationship_type_rejects_reverse_label_for_existing_symmetric_type(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        db_session.add(
            RelationshipTypeDefinition(
                id=uuid4(),
                campaign_id=test_campaign.id,
                key="sibling_oath",
                label="sibling oath",
                family="social",
                reverse_label=None,
                is_symmetric=True,
                allowed_source_types=["person"],
                allowed_target_types=["person"],
            )
        )
        db_session.commit()

    response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}/relationship-types/sibling_oath",
        json={"reverse_label": "bound by oath"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Symmetric relationship types cannot define a reverse label."
    }


def test_delete_custom_relationship_type_rejects_used_type(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        entity_a = Entity(campaign_id=test_campaign.id, type="person", name="Martha")
        entity_b = Entity(campaign_id=test_campaign.id, type="person", name="Rick")
        db_session.add_all([entity_a, entity_b])
        db_session.flush()
        db_session.add(
            RelationshipTypeDefinition(
                id=uuid4(),
                campaign_id=test_campaign.id,
                key="bodyguard_of",
                label="bodyguard of",
                family="social",
                reverse_label="guarded by",
                is_symmetric=False,
                allowed_source_types=["person"],
                allowed_target_types=["person"],
            )
        )
        db_session.add(
            Relationship(
                campaign_id=test_campaign.id,
                source_entity=entity_a,
                target_entity=entity_b,
                relationship_type="bodyguard_of",
                lifecycle_status="current",
                visibility_status="public",
                certainty_status="confirmed",
            )
        )
        db_session.commit()

    response = api_request(
        "DELETE",
        f"/api/campaigns/{test_campaign.id}/relationship-types/bodyguard_of",
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Relationship type cannot be deleted while it is in use."}


def test_create_relationship_returns_created_record_with_catalog_metadata(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        source_entity = Entity(campaign_id=test_campaign.id, type="person", name="Tarannon")
        target_entity = Entity(campaign_id=test_campaign.id, type="person", name="Civu")
        db_session.add_all([source_entity, target_entity])
        db_session.commit()
        db_session.refresh(source_entity)
        db_session.refresh(target_entity)

    response = api_request(
        "POST",
        f"/api/campaigns/{test_campaign.id}/relationships",
        json={
            "source_entity_id": str(source_entity.id),
            "target_entity_id": str(target_entity.id),
            "relationship_type": "spouse_of",
            "lifecycle_status": "current",
            "visibility_status": "secret",
            "certainty_status": "confirmed",
            "notes": "They conceal the marriage from the court.",
        },
    )

    assert response.status_code == 201
    assert response.json()["relationship_type"] == "spouse_of"
    assert response.json()["relationship_family"] == "romance"
    assert response.json()["forward_label"] == "spouse of"
    assert response.json()["reverse_label"] == "spouse of"
    assert response.json()["visibility_status"] == "secret"


def test_build_relationship_response_payloads_reuses_descriptor_for_repeated_custom_type(
    db_session_factory,
    monkeypatch,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        source_entity = Entity(campaign_id=test_campaign.id, type="person", name="Tarannon")
        target_entity = Entity(campaign_id=test_campaign.id, type="person", name="Civu")
        third_entity = Entity(campaign_id=test_campaign.id, type="person", name="Ilya")
        db_session.add_all([source_entity, target_entity, third_entity])
        db_session.flush()
        db_session.add(
            RelationshipTypeDefinition(
                id=uuid4(),
                campaign_id=test_campaign.id,
                key="bodyguard_of",
                label="bodyguard of",
                family="social",
                reverse_label="guarded by",
                is_symmetric=False,
                allowed_source_types=["person"],
                allowed_target_types=["person"],
            )
        )
        first_relationship = Relationship(
            campaign_id=test_campaign.id,
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type="bodyguard_of",
            lifecycle_status="current",
            visibility_status="public",
            certainty_status="confirmed",
        )
        second_relationship = Relationship(
            campaign_id=test_campaign.id,
            source_entity=third_entity,
            target_entity=target_entity,
            relationship_type="bodyguard_of",
            lifecycle_status="current",
            visibility_status="public",
            certainty_status="confirmed",
        )
        db_session.add_all([first_relationship, second_relationship])
        db_session.commit()

        descriptor_lookup_count = 0
        original_get_relationship_type_descriptor = services.relationship_service.get_relationship_type_descriptor

        def counting_get_relationship_type_descriptor(*args, **kwargs):
            nonlocal descriptor_lookup_count
            descriptor_lookup_count += 1
            return original_get_relationship_type_descriptor(*args, **kwargs)

        monkeypatch.setattr(
            services.relationship_service,
            "get_relationship_type_descriptor",
            counting_get_relationship_type_descriptor,
        )

        listed_relationships = services.relationship_service.list_relationships(
            db_session,
            campaign_id=test_campaign.id,
        )

        payloads = services.relationship_service.build_relationship_response_payloads(
            db_session,
            relationships=listed_relationships,
        )

    assert [payload["relationship_type"] for payload in payloads] == ["bodyguard_of", "bodyguard_of"]
    assert descriptor_lookup_count == 1


def test_create_relationship_rejects_cross_campaign_target_entity(
    api_request,
    db_session_factory,
    test_owner,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        second_campaign = Campaign(owner_id=test_owner.id, name="Second Campaign")
        db_session.add(second_campaign)
        db_session.flush()
        source_entity = Entity(campaign_id=test_campaign.id, type="person", name="Tarannon")
        foreign_target_entity = Entity(campaign_id=second_campaign.id, type="person", name="Civu")
        db_session.add_all([source_entity, foreign_target_entity])
        db_session.commit()
        db_session.refresh(source_entity)
        db_session.refresh(foreign_target_entity)

    response = api_request(
        "POST",
        f"/api/campaigns/{test_campaign.id}/relationships",
        json={
            "source_entity_id": str(source_entity.id),
            "target_entity_id": str(foreign_target_entity.id),
            "relationship_type": "spouse_of",
            "lifecycle_status": "current",
            "visibility_status": "public",
            "certainty_status": "confirmed",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Target entity not found."}


def test_create_relationship_rejects_invalid_type_pair(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        source_entity = Entity(campaign_id=test_campaign.id, type="organization", name="The Choir")
        target_entity = Entity(campaign_id=test_campaign.id, type="location", name="Gawo")
        db_session.add_all([source_entity, target_entity])
        db_session.commit()
        db_session.refresh(source_entity)
        db_session.refresh(target_entity)

    response = api_request(
        "POST",
        f"/api/campaigns/{test_campaign.id}/relationships",
        json={
            "source_entity_id": str(source_entity.id),
            "target_entity_id": str(target_entity.id),
            "relationship_type": "spouse_of",
            "lifecycle_status": "current",
            "visibility_status": "public",
            "certainty_status": "confirmed",
        },
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]
        == "Relationship type is not valid for the source and target entity types."
    )


def test_create_relationship_rejects_inverse_duplicate_for_symmetric_type(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        first_entity = Entity(campaign_id=test_campaign.id, type="person", name="Jo")
        second_entity = Entity(campaign_id=test_campaign.id, type="person", name="Mika")
        db_session.add_all([first_entity, second_entity])
        db_session.flush()
        db_session.add(
            Relationship(
                campaign_id=test_campaign.id,
                source_entity=first_entity,
                target_entity=second_entity,
                relationship_type="sibling_of",
                lifecycle_status="current",
                visibility_status="public",
                certainty_status="confirmed",
            )
        )
        db_session.commit()
        db_session.refresh(first_entity)
        db_session.refresh(second_entity)

    response = api_request(
        "POST",
        f"/api/campaigns/{test_campaign.id}/relationships",
        json={
            "source_entity_id": str(second_entity.id),
            "target_entity_id": str(first_entity.id),
            "relationship_type": "sibling_of",
            "lifecycle_status": "current",
            "visibility_status": "public",
            "certainty_status": "confirmed",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Symmetric relationship already exists for these entities."
    }


def test_list_relationships_supports_type_and_family_filters(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        tarannon = Entity(campaign_id=test_campaign.id, type="person", name="Tarannon")
        civu = Entity(campaign_id=test_campaign.id, type="person", name="Civu")
        underground = Entity(campaign_id=test_campaign.id, type="organization", name="Underground")
        db_session.add_all([tarannon, civu, underground])
        db_session.flush()
        db_session.add_all(
            [
                Relationship(
                    campaign_id=test_campaign.id,
                    source_entity=tarannon,
                    target_entity=civu,
                    relationship_type="spouse_of",
                    lifecycle_status="current",
                    visibility_status="public",
                    certainty_status="confirmed",
                ),
                Relationship(
                    campaign_id=test_campaign.id,
                    source_entity=civu,
                    target_entity=underground,
                    relationship_type="works_for",
                    lifecycle_status="current",
                    visibility_status="secret",
                    certainty_status="rumored",
                ),
            ]
        )
        db_session.commit()

    response = api_request(
        "GET",
        f"/api/campaigns/{test_campaign.id}/relationships",
        params={"type": "spouse_of", "family": "romance"},
    )

    assert response.status_code == 200
    assert [
        listed_relationship["relationship_type"] for listed_relationship in response.json()
    ] == ["spouse_of"]


def test_list_relationships_supports_family_only_filter(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        tarannon = Entity(campaign_id=test_campaign.id, type="person", name="Tarannon")
        civu = Entity(campaign_id=test_campaign.id, type="person", name="Civu")
        underground = Entity(campaign_id=test_campaign.id, type="organization", name="Underground")
        db_session.add_all([tarannon, civu, underground])
        db_session.flush()
        db_session.add_all(
            [
                Relationship(
                    campaign_id=test_campaign.id,
                    source_entity=tarannon,
                    target_entity=civu,
                    relationship_type="spouse_of",
                    lifecycle_status="current",
                    visibility_status="public",
                    certainty_status="confirmed",
                ),
                Relationship(
                    campaign_id=test_campaign.id,
                    source_entity=civu,
                    target_entity=underground,
                    relationship_type="works_for",
                    lifecycle_status="current",
                    visibility_status="secret",
                    certainty_status="rumored",
                ),
            ]
        )
        db_session.commit()

    response = api_request(
        "GET",
        f"/api/campaigns/{test_campaign.id}/relationships",
        params={"family": "romance"},
    )

    assert response.status_code == 200
    assert [
        listed_relationship["relationship_type"] for listed_relationship in response.json()
    ] == ["spouse_of"]


def test_list_relationships_rejects_mismatched_type_and_family_filters(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        source_entity = Entity(campaign_id=test_campaign.id, type="person", name="Tarannon")
        target_entity = Entity(campaign_id=test_campaign.id, type="person", name="Civu")
        db_session.add_all([source_entity, target_entity])
        db_session.flush()
        db_session.add(
            Relationship(
                campaign_id=test_campaign.id,
                source_entity=source_entity,
                target_entity=target_entity,
                relationship_type="spouse_of",
                lifecycle_status="current",
                visibility_status="public",
                certainty_status="confirmed",
            )
        )
        db_session.commit()

    response = api_request(
        "GET",
        f"/api/campaigns/{test_campaign.id}/relationships",
        params={"type": "spouse_of", "family": "social"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Relationship type does not belong to the requested relationship family."
    }


def test_get_update_and_delete_relationship_flow(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        source_entity = Entity(campaign_id=test_campaign.id, type="person", name="Tarannon")
        target_entity = Entity(campaign_id=test_campaign.id, type="location", name="Gawo")
        db_session.add_all([source_entity, target_entity])
        db_session.flush()
        stored_relationship = Relationship(
            campaign_id=test_campaign.id,
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type="lives_in",
            lifecycle_status="current",
            visibility_status="public",
            certainty_status="confirmed",
            notes="Original note",
        )
        db_session.add(stored_relationship)
        db_session.commit()
        db_session.refresh(stored_relationship)
        stored_relationship_id = stored_relationship.id

    get_response = api_request(
        "GET",
        f"/api/campaigns/{test_campaign.id}/relationships/{stored_relationship_id}",
    )

    assert get_response.status_code == 200
    assert get_response.json()["notes"] == "Original note"
    assert get_response.json()["relationship_family"] == "location"

    update_response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}/relationships/{stored_relationship_id}",
        json={
            "lifecycle_status": "former",
            "visibility_status": "secret",
            "certainty_status": "rumored",
            "notes": "Updated note",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["lifecycle_status"] == "former"
    assert update_response.json()["visibility_status"] == "secret"
    assert update_response.json()["certainty_status"] == "rumored"
    assert update_response.json()["notes"] == "Updated note"

    delete_response = api_request(
        "DELETE",
        f"/api/campaigns/{test_campaign.id}/relationships/{stored_relationship_id}",
    )

    assert delete_response.status_code == 204

    missing_response = api_request(
        "GET",
        f"/api/campaigns/{test_campaign.id}/relationships/{stored_relationship_id}",
    )
    assert missing_response.status_code == 404


def test_update_relationship_rejects_invalid_type_pair(
    api_request,
    db_session_factory,
    test_campaign: Campaign,
) -> None:
    with db_session_factory() as db_session:
        source_entity = Entity(campaign_id=test_campaign.id, type="organization", name="The Choir")
        target_entity = Entity(campaign_id=test_campaign.id, type="location", name="Gawo")
        db_session.add_all([source_entity, target_entity])
        db_session.flush()
        stored_relationship = Relationship(
            campaign_id=test_campaign.id,
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type="located_in",
            lifecycle_status="current",
            visibility_status="public",
            certainty_status="confirmed",
        )
        db_session.add(stored_relationship)
        db_session.commit()
        db_session.refresh(stored_relationship)

    response = api_request(
        "PATCH",
        f"/api/campaigns/{test_campaign.id}/relationships/{stored_relationship.id}",
        json={"relationship_type": "spouse_of"},
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]
        == "Relationship type is not valid for the source and target entity types."
    )
