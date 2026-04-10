from __future__ import annotations

from collections.abc import Iterable

from app.enums import EntityType, normalize_str_enum_value


def validate_entity_type(entity_type: str) -> EntityType:
    return normalize_str_enum_value(EntityType, entity_type)


def validate_entity_types(entity_types: Iterable[str]) -> None:
    for entity_type in entity_types:
        validate_entity_type(entity_type)
