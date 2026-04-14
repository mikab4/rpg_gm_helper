from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import (
    Campaign,
    Entity,
    ExtractionCandidate,
    ExtractionJob,
    Owner,
    Relationship,
    SessionNote,
    SourceDocument,
)
from app.models.relationship_type_definition import RelationshipTypeDefinition
from tests.pg_test_support import upgraded_postgres_test_engine


@pytest.fixture
def postgres_session(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> Session:
    with upgraded_postgres_test_engine(
        monkeypatch=monkeypatch,
        settings=postgres_test_settings,
    ) as engine:
        with Session(engine) as session:
            yield session


def test_can_persist_and_retrieve_core_records(postgres_session: Session) -> None:
    # Arrange
    owner = Owner(email="gm@example.com", display_name="Local GM")
    campaign = Campaign(owner=owner, name="Shadows of Glass", description="Urban intrigue")
    session_note = SessionNote(
        campaign=campaign,
        session_number=1,
        session_label="The First Omen",
        played_on=date(2026, 4, 4),
        summary="The party investigated the broken observatory.",
    )
    source_document = SourceDocument(
        campaign=campaign,
        session_note=session_note,
        title="GM recap",
        truth_status="canonical",
        raw_text="The party met Magistrate Ilya in the observatory ruins.",
        metadata_={"source": "gm_recap"},
    )
    extraction_job = ExtractionJob(
        campaign=campaign,
        source_document=source_document,
        status="completed",
        extractor_kind="rules",
        completed_at=datetime(2026, 4, 4, 10, 30, tzinfo=UTC),
    )
    candidate = ExtractionCandidate(
        campaign=campaign,
        extraction_job=extraction_job,
        candidate_type="entity",
        payload={"type": "person", "name": "Magistrate Ilya"},
        status="pending",
        provenance_excerpt="met Magistrate Ilya in the observatory ruins",
    )
    entity_a = Entity(
        campaign=campaign,
        type="person",
        name="Magistrate Ilya",
        summary="A city official with a hidden agenda.",
        metadata_={"faction": "City Watch"},
        source_document=source_document,
        provenance_excerpt="met Magistrate Ilya",
    )
    entity_b = Entity(
        campaign=campaign,
        type="location",
        name="Broken Observatory",
        source_document=source_document,
    )
    relationship = Relationship(
        campaign=campaign,
        source_entity=entity_a,
        target_entity=entity_b,
        relationship_type="investigates",
        lifecycle_status="current",
        visibility_status="public",
        certainty_status="confirmed",
        notes="Ilya was seen inspecting the ruins.",
        confidence=0.8,
        source_document=source_document,
        provenance_data={"candidate_id": str(uuid4())},
    )

    postgres_session.add_all(
        [
            owner,
            campaign,
            session_note,
            source_document,
            extraction_job,
            candidate,
            entity_a,
            entity_b,
            relationship,
        ]
    )

    # Act
    postgres_session.commit()

    stored_campaign = postgres_session.get(Campaign, campaign.id)
    stored_note = postgres_session.get(SessionNote, session_note.id)
    stored_document = postgres_session.get(SourceDocument, source_document.id)
    stored_job = postgres_session.get(ExtractionJob, extraction_job.id)
    stored_candidate = postgres_session.get(ExtractionCandidate, candidate.id)
    stored_relationship = postgres_session.get(Relationship, relationship.id)

    # Assert
    assert stored_campaign is not None
    assert stored_campaign.owner_id == owner.id
    assert stored_note is not None
    assert stored_note.campaign_id == campaign.id
    assert stored_document is not None
    assert stored_document.session_note_id == session_note.id
    assert stored_job is not None
    assert stored_job.source_document_id == source_document.id
    assert stored_candidate is not None
    assert stored_candidate.extraction_job_id == extraction_job.id
    assert stored_relationship is not None
    assert stored_relationship.source_entity_id == entity_a.id
    assert stored_relationship.target_entity_id == entity_b.id
    assert stored_relationship.lifecycle_status == "current"
    assert stored_relationship.visibility_status == "public"
    assert stored_relationship.certainty_status == "confirmed"


def test_orm_inserts_apply_json_defaults_consistently(postgres_session: Session) -> None:
    # Arrange
    owner = Owner(email="gm@example.com")
    campaign = Campaign(owner=owner, name="Shadows of Glass")
    source_document = SourceDocument(
        campaign=campaign,
        truth_status="canonical",
        raw_text="Raw text only",
    )
    extraction_job = ExtractionJob(
        campaign=campaign,
        source_document=source_document,
        status="pending",
        extractor_kind="rules",
    )
    candidate = ExtractionCandidate(
        campaign=campaign,
        extraction_job=extraction_job,
        candidate_type="entity",
        payload={"name": "Magistrate Ilya"},
        status="pending",
    )
    entity = Entity(
        campaign=campaign,
        type="person",
        name="Magistrate Ilya",
        source_document=source_document,
    )
    relationship_type_definition = RelationshipTypeDefinition(
        campaign=campaign,
        key="bodyguard_of",
        label="bodyguard of",
        family="social",
        reverse_label="guarded by",
        is_symmetric=False,
        allowed_source_types=["person"],
        allowed_target_types=["person"],
    )
    relationship = Relationship(
        campaign=campaign,
        source_entity=entity,
        target_entity=entity,
        relationship_type="knows",
        source_document=source_document,
    )

    postgres_session.add_all(
        [
            owner,
            campaign,
            source_document,
            extraction_job,
            candidate,
            entity,
            relationship_type_definition,
            relationship,
        ]
    )

    # Act
    postgres_session.commit()

    stored_document = postgres_session.get(SourceDocument, source_document.id)
    stored_candidate = postgres_session.get(ExtractionCandidate, candidate.id)
    stored_entity = postgres_session.get(Entity, entity.id)
    stored_relationship = postgres_session.get(Relationship, relationship.id)
    stored_relationship_type_definition = postgres_session.get(
        RelationshipTypeDefinition,
        relationship_type_definition.id,
    )

    # Assert
    assert stored_document is not None
    assert stored_document.metadata_ == {}
    assert stored_candidate is not None
    assert stored_candidate.provenance_data == {}
    assert stored_entity is not None
    assert stored_entity.metadata_ == {}
    assert stored_entity.provenance_data == {}
    assert stored_relationship_type_definition is not None
    assert stored_relationship_type_definition.allowed_source_types == ["person"]
    assert stored_relationship_type_definition.allowed_target_types == ["person"]
    assert stored_relationship is not None
    assert stored_relationship.provenance_data == {}
    assert stored_relationship.lifecycle_status == "current"
    assert stored_relationship.visibility_status == "public"
    assert stored_relationship.certainty_status == "confirmed"


def test_updated_at_changes_on_orm_update(postgres_session: Session) -> None:
    # Arrange
    owner = Owner(email="gm@example.com")
    campaign = Campaign(owner=owner, name="Shadows of Glass")
    source_document = SourceDocument(
        campaign=campaign,
        truth_status="canonical",
        raw_text="Original text",
    )

    postgres_session.add_all([owner, campaign, source_document])
    postgres_session.commit()

    original_updated_at = source_document.updated_at

    # Act
    source_document.raw_text = "Updated text"
    postgres_session.commit()
    postgres_session.refresh(source_document)

    # Assert
    assert source_document.updated_at > original_updated_at


def test_relationship_rejects_confidence_below_zero(postgres_session: Session) -> None:
    # Arrange
    owner = Owner(email="gm@example.com")
    campaign = Campaign(owner=owner, name="Shadows of Glass")
    entity_a = Entity(campaign=campaign, type="person", name="Magistrate Ilya")
    entity_b = Entity(campaign=campaign, type="location", name="Broken Observatory")

    postgres_session.add_all([owner, campaign, entity_a, entity_b])
    postgres_session.commit()

    postgres_session.add(
        Relationship(
            campaign=campaign,
            source_entity=entity_a,
            target_entity=entity_b,
            relationship_type="knows",
            confidence=Decimal("-0.01"),
        )
    )

    # Act / Assert
    with pytest.raises(IntegrityError):
        postgres_session.commit()
    postgres_session.rollback()


def test_relationship_rejects_confidence_above_one(postgres_session: Session) -> None:
    # Arrange
    owner = Owner(email="gm@example.com")
    campaign = Campaign(owner=owner, name="Shadows of Glass")
    entity_a = Entity(campaign=campaign, type="person", name="Magistrate Ilya")
    entity_b = Entity(campaign=campaign, type="location", name="Broken Observatory")

    postgres_session.add_all([owner, campaign, entity_a, entity_b])
    postgres_session.commit()

    postgres_session.add(
        Relationship(
            campaign=campaign,
            source_entity=entity_a,
            target_entity=entity_b,
            relationship_type="knows",
            confidence=Decimal("1.01"),
        )
    )

    # Act / Assert
    with pytest.raises(IntegrityError):
        postgres_session.commit()
    postgres_session.rollback()


def test_campaign_name_must_be_unique_per_owner(postgres_session: Session) -> None:
    # Arrange
    owner = Owner(email="gm@example.com")
    postgres_session.add(owner)
    postgres_session.flush()

    postgres_session.add_all(
        [
            Campaign(owner_id=owner.id, name="Shadows of Glass"),
            Campaign(owner_id=owner.id, name="Shadows of Glass"),
        ]
    )

    # Act / Assert
    with pytest.raises(IntegrityError):
        postgres_session.commit()
    postgres_session.rollback()


def test_session_note_requires_number_or_label(postgres_session: Session) -> None:
    # Arrange
    owner = Owner(email="gm@example.com")
    campaign = Campaign(owner=owner, name="Shadows of Glass")
    postgres_session.add_all([owner, campaign])
    postgres_session.flush()

    postgres_session.add(SessionNote(campaign_id=campaign.id))

    # Act / Assert
    with pytest.raises(IntegrityError):
        postgres_session.commit()
    postgres_session.rollback()


def test_session_number_must_be_unique_within_campaign(postgres_session: Session) -> None:
    # Arrange
    owner = Owner(email="gm@example.com")
    campaign = Campaign(owner=owner, name="Shadows of Glass")
    postgres_session.add_all([owner, campaign])
    postgres_session.flush()

    postgres_session.add_all(
        [
            SessionNote(campaign_id=campaign.id, session_number=7),
            SessionNote(campaign_id=campaign.id, session_number=7, session_label="Seven again"),
        ]
    )

    # Act / Assert
    with pytest.raises(IntegrityError):
        postgres_session.commit()
    postgres_session.rollback()
