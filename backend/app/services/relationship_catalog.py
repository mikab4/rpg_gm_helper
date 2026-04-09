from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.relationship_type_definition import RelationshipTypeDefinition
from app.schemas.relationship_types import normalize_relationship_type_key


@dataclass(frozen=True)
class RelationshipTypeDescriptor:
    key: str
    label: str
    family: str
    reverse_label: str
    is_symmetric: bool
    allowed_source_types: tuple[str, ...]
    allowed_target_types: tuple[str, ...]
    is_custom: bool
    campaign_id: UUID | None = None
    id: UUID | None = None
    created_at: object | None = None
    updated_at: object | None = None


BUILT_IN_RELATIONSHIP_TYPES: dict[str, RelationshipTypeDescriptor] = {
    "parent_of": RelationshipTypeDescriptor(
        key="parent_of",
        label="parent of",
        family="family",
        reverse_label="child of",
        is_symmetric=False,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "sibling_of": RelationshipTypeDescriptor(
        key="sibling_of",
        label="sibling of",
        family="family",
        reverse_label="sibling of",
        is_symmetric=True,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "adoptive_parent_of": RelationshipTypeDescriptor(
        key="adoptive_parent_of",
        label="adoptive parent of",
        family="family",
        reverse_label="adoptive child of",
        is_symmetric=False,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "aunt_or_uncle_of": RelationshipTypeDescriptor(
        key="aunt_or_uncle_of",
        label="aunt or uncle of",
        family="family",
        reverse_label="niece or nephew of",
        is_symmetric=False,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "cousin_of": RelationshipTypeDescriptor(
        key="cousin_of",
        label="cousin of",
        family="family",
        reverse_label="cousin of",
        is_symmetric=True,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "spouse_of": RelationshipTypeDescriptor(
        key="spouse_of",
        label="spouse of",
        family="romance",
        reverse_label="spouse of",
        is_symmetric=True,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "betrothed_to": RelationshipTypeDescriptor(
        key="betrothed_to",
        label="betrothed to",
        family="romance",
        reverse_label="betrothed to",
        is_symmetric=True,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "lover_of": RelationshipTypeDescriptor(
        key="lover_of",
        label="lover of",
        family="romance",
        reverse_label="lover of",
        is_symmetric=True,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "affair_with": RelationshipTypeDescriptor(
        key="affair_with",
        label="affair with",
        family="romance",
        reverse_label="affair with",
        is_symmetric=True,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "friend_of": RelationshipTypeDescriptor(
        key="friend_of",
        label="friend of",
        family="social",
        reverse_label="friend of",
        is_symmetric=True,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "rival_of": RelationshipTypeDescriptor(
        key="rival_of",
        label="rival of",
        family="social",
        reverse_label="rival of",
        is_symmetric=True,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "mentor_of": RelationshipTypeDescriptor(
        key="mentor_of",
        label="mentor of",
        family="social",
        reverse_label="mentored by",
        is_symmetric=False,
        allowed_source_types=("person",),
        allowed_target_types=("person",),
        is_custom=False,
    ),
    "member_of": RelationshipTypeDescriptor(
        key="member_of",
        label="member of",
        family="organization",
        reverse_label="has member",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "other"),
        allowed_target_types=("organization",),
        is_custom=False,
    ),
    "leader_of": RelationshipTypeDescriptor(
        key="leader_of",
        label="leader of",
        family="organization",
        reverse_label="led by",
        is_symmetric=False,
        allowed_source_types=("person",),
        allowed_target_types=("organization",),
        is_custom=False,
    ),
    "advisor_to": RelationshipTypeDescriptor(
        key="advisor_to",
        label="advisor to",
        family="organization",
        reverse_label="advised by",
        is_symmetric=False,
        allowed_source_types=("person",),
        allowed_target_types=("person", "organization"),
        is_custom=False,
    ),
    "works_for": RelationshipTypeDescriptor(
        key="works_for",
        label="works for",
        family="organization",
        reverse_label="employs",
        is_symmetric=False,
        allowed_source_types=("person", "organization"),
        allowed_target_types=("organization", "person"),
        is_custom=False,
    ),
    "governs": RelationshipTypeDescriptor(
        key="governs",
        label="governs",
        family="political",
        reverse_label="governed by",
        is_symmetric=False,
        allowed_source_types=("person", "organization"),
        allowed_target_types=("location",),
        is_custom=False,
    ),
    "lives_in": RelationshipTypeDescriptor(
        key="lives_in",
        label="lives in",
        family="location",
        reverse_label="inhabited by",
        is_symmetric=False,
        allowed_source_types=("person",),
        allowed_target_types=("location",),
        is_custom=False,
    ),
    "based_in": RelationshipTypeDescriptor(
        key="based_in",
        label="based in",
        family="location",
        reverse_label="base of",
        is_symmetric=False,
        allowed_source_types=("organization", "other"),
        allowed_target_types=("location",),
        is_custom=False,
    ),
    "from_place": RelationshipTypeDescriptor(
        key="from_place",
        label="from place",
        family="location",
        reverse_label="origin place of",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "other"),
        allowed_target_types=("location",),
        is_custom=False,
    ),
    "located_in": RelationshipTypeDescriptor(
        key="located_in",
        label="located in",
        family="location",
        reverse_label="contains",
        is_symmetric=False,
        allowed_source_types=("location",),
        allowed_target_types=("location",),
        is_custom=False,
    ),
    "enemy_of": RelationshipTypeDescriptor(
        key="enemy_of",
        label="enemy of",
        family="conflict",
        reverse_label="enemy of",
        is_symmetric=True,
        allowed_source_types=("person", "organization", "deity", "other"),
        allowed_target_types=("person", "organization", "deity", "other"),
        is_custom=False,
    ),
    "opposes": RelationshipTypeDescriptor(
        key="opposes",
        label="opposes",
        family="conflict",
        reverse_label="opposed by",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "deity", "other"),
        allowed_target_types=("person", "organization", "deity", "other", "location"),
        is_custom=False,
    ),
    "hunting": RelationshipTypeDescriptor(
        key="hunting",
        label="hunting",
        family="conflict",
        reverse_label="hunted by",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "other"),
        allowed_target_types=("person", "organization", "other"),
        is_custom=False,
    ),
    "ally_of": RelationshipTypeDescriptor(
        key="ally_of",
        label="ally of",
        family="influence",
        reverse_label="ally of",
        is_symmetric=True,
        allowed_source_types=("person", "organization", "deity", "other"),
        allowed_target_types=("person", "organization", "deity", "other"),
        is_custom=False,
    ),
    "serves": RelationshipTypeDescriptor(
        key="serves",
        label="serves",
        family="influence",
        reverse_label="served by",
        is_symmetric=False,
        allowed_source_types=("person", "organization"),
        allowed_target_types=("person", "organization", "deity"),
        is_custom=False,
    ),
    "disciple_of": RelationshipTypeDescriptor(
        key="disciple_of",
        label="disciple of",
        family="influence",
        reverse_label="has disciple",
        is_symmetric=False,
        allowed_source_types=("person", "organization"),
        allowed_target_types=("person", "deity"),
        is_custom=False,
    ),
    "worships": RelationshipTypeDescriptor(
        key="worships",
        label="worships",
        family="influence",
        reverse_label="worshipped by",
        is_symmetric=False,
        allowed_source_types=("person", "organization"),
        allowed_target_types=("deity",),
        is_custom=False,
    ),
    "patron_of": RelationshipTypeDescriptor(
        key="patron_of",
        label="patron of",
        family="influence",
        reverse_label="patron of",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "deity"),
        allowed_target_types=("person", "organization"),
        is_custom=False,
    ),
    "corrupted_by": RelationshipTypeDescriptor(
        key="corrupted_by",
        label="corrupted by",
        family="influence",
        reverse_label="corrupts",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "item", "other"),
        allowed_target_types=("person", "organization", "deity", "item", "other"),
        is_custom=False,
    ),
    "participated_in": RelationshipTypeDescriptor(
        key="participated_in",
        label="participated in",
        family="event",
        reverse_label="had participant",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "other"),
        allowed_target_types=("event",),
        is_custom=False,
    ),
    "caused": RelationshipTypeDescriptor(
        key="caused",
        label="caused",
        family="event",
        reverse_label="caused by",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "deity", "other"),
        allowed_target_types=("event", "other"),
        is_custom=False,
    ),
    "witnessed": RelationshipTypeDescriptor(
        key="witnessed",
        label="witnessed",
        family="event",
        reverse_label="witnessed by",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "other"),
        allowed_target_types=("event", "other"),
        is_custom=False,
    ),
    "survived": RelationshipTypeDescriptor(
        key="survived",
        label="survived",
        family="event",
        reverse_label="survived by",
        is_symmetric=False,
        allowed_source_types=("person", "organization", "other"),
        allowed_target_types=("event", "other"),
        is_custom=False,
    ),
}


def normalize_relationship_type(relationship_type_key: str) -> str:
    return normalize_relationship_type_key(relationship_type_key.replace("_", " "))


def build_descriptor_from_custom_type(
    custom_type_definition: RelationshipTypeDefinition,
) -> RelationshipTypeDescriptor:
    reverse_label = (
        custom_type_definition.label
        if custom_type_definition.is_symmetric
        else custom_type_definition.reverse_label or custom_type_definition.label
    )
    return RelationshipTypeDescriptor(
        key=custom_type_definition.key,
        label=custom_type_definition.label,
        family=custom_type_definition.family,
        reverse_label=reverse_label,
        is_symmetric=custom_type_definition.is_symmetric,
        allowed_source_types=tuple(custom_type_definition.allowed_source_types),
        allowed_target_types=tuple(custom_type_definition.allowed_target_types),
        is_custom=True,
        campaign_id=custom_type_definition.campaign_id,
        id=custom_type_definition.id,
        created_at=custom_type_definition.created_at,
        updated_at=custom_type_definition.updated_at,
    )


def list_relationship_type_descriptors(
    db_session: Session,
    *,
    campaign_id: UUID | None = None,
) -> list[RelationshipTypeDescriptor]:
    descriptors = list(BUILT_IN_RELATIONSHIP_TYPES.values())
    if campaign_id is not None:
        custom_type_definitions = list(
            db_session.scalars(
                select(RelationshipTypeDefinition)
                .where(RelationshipTypeDefinition.campaign_id == campaign_id)
                .order_by(RelationshipTypeDefinition.family, RelationshipTypeDefinition.label)
            )
        )
        descriptors.extend(
            build_descriptor_from_custom_type(custom_type_definition)
            for custom_type_definition in custom_type_definitions
        )
    return sorted(descriptors, key=lambda descriptor: (descriptor.family, descriptor.label))


def get_relationship_type_descriptor(
    db_session: Session,
    *,
    relationship_type_key: str,
    campaign_id: UUID | None = None,
) -> RelationshipTypeDescriptor | None:
    normalized_type_key = normalize_relationship_type(relationship_type_key)
    built_in_descriptor = BUILT_IN_RELATIONSHIP_TYPES.get(normalized_type_key)
    if built_in_descriptor is not None:
        return built_in_descriptor

    if campaign_id is None:
        return None

    custom_type_definition = db_session.scalar(
        select(RelationshipTypeDefinition).where(
            RelationshipTypeDefinition.campaign_id == campaign_id,
            RelationshipTypeDefinition.key == normalized_type_key,
        )
    )
    if custom_type_definition is None:
        return None
    return build_descriptor_from_custom_type(custom_type_definition)
