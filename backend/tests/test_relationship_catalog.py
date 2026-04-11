from __future__ import annotations

from uuid import uuid4

from app.models.relationship_type_definition import RelationshipTypeDefinition
from app.services.relationship_catalog import build_descriptor_from_custom_type


def test_build_descriptor_from_custom_type_uses_stored_reverse_label_for_asymmetric_type() -> None:
    custom_type_definition = RelationshipTypeDefinition(
        id=uuid4(),
        campaign_id=uuid4(),
        key="bodyguard_of",
        label="bodyguard of",
        family="social",
        reverse_label="guarded by",
        is_symmetric=False,
        allowed_source_types=["person"],
        allowed_target_types=["person"],
    )

    descriptor = build_descriptor_from_custom_type(custom_type_definition)

    assert descriptor.reverse_label == "guarded by"
