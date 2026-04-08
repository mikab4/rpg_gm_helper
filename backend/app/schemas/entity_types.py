from __future__ import annotations

from collections.abc import Iterable

ALLOWED_ENTITY_TYPES = {
    "npc",
    "location",
    "artifact",
    "faction",
    "event",
    "lore",
}


def validate_entity_type(entity_type: str) -> str:
    normalized_entity_type = entity_type.strip().lower()

    if normalized_entity_type not in ALLOWED_ENTITY_TYPES:
        allowed_values = ", ".join(sorted(ALLOWED_ENTITY_TYPES))
        raise ValueError(f"Entity type must be one of: {allowed_values}.")

    return normalized_entity_type


def validate_entity_types(entity_types: Iterable[str]) -> None:
    for entity_type in entity_types:
        validate_entity_type(entity_type)
