from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.api.routes.relationship_types import build_relationship_type_response
from app.enums import EntityType, RelationshipFamily
from app.models.relationship_type_definition import RelationshipTypeDefinition
from app.services.relationship_catalog import RelationshipTypeDescriptor


def test_build_relationship_type_response_accepts_custom_definition_and_descriptor() -> None:
    created_at = datetime(2026, 4, 11, tzinfo=UTC)
    updated_at = datetime(2026, 4, 12, tzinfo=UTC)
    custom_definition = RelationshipTypeDefinition(
        id=uuid4(),
        campaign_id=uuid4(),
        key="bodyguard_of",
        label="bodyguard of",
        family="social",
        reverse_label="guarded by",
        is_symmetric=False,
        allowed_source_types=["person"],
        allowed_target_types=["person"],
        created_at=created_at,
        updated_at=updated_at,
    )
    built_in_descriptor = RelationshipTypeDescriptor(
        key="sibling_of",
        label="sibling of",
        family=RelationshipFamily.FAMILY,
        reverse_label="sibling of",
        is_symmetric=True,
        allowed_source_types=(EntityType.PERSON,),
        allowed_target_types=(EntityType.PERSON,),
        is_custom=False,
    )

    custom_response = build_relationship_type_response(custom_definition, is_custom=True)
    built_in_response = build_relationship_type_response(
        built_in_descriptor,
        is_custom=built_in_descriptor.is_custom,
    )

    assert custom_response.key == "bodyguard_of"
    assert custom_response.family_label == "Social"
    assert custom_response.reverse_label == "guarded by"
    assert custom_response.is_custom is True
    assert custom_response.created_at == created_at
    assert custom_response.updated_at == updated_at

    assert built_in_response.key == "sibling_of"
    assert built_in_response.family_label == "Family"
    assert built_in_response.reverse_label == "sibling of"
    assert built_in_response.is_custom is False
