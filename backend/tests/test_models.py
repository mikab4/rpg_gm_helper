from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
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


def test_relationship_model_uses_entity_relationships_table() -> None:
    assert Relationship.__tablename__ == "entity_relationships"


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    with factory() as session:
        yield session
    engine.dispose()


def test_can_persist_and_retrieve_core_records(session: Session) -> None:
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
        payload={"type": "npc", "name": "Magistrate Ilya"},
        status="pending",
        provenance_excerpt="met Magistrate Ilya in the observatory ruins",
    )
    entity_a = Entity(
        campaign=campaign,
        type="npc",
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
        notes="Ilya was seen inspecting the ruins.",
        confidence=0.8,
        source_document=source_document,
        provenance_data={"candidate_id": str(uuid4())},
    )

    session.add_all(
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
    session.commit()

    stored_campaign = session.get(Campaign, campaign.id)
    stored_note = session.get(SessionNote, session_note.id)
    stored_document = session.get(SourceDocument, source_document.id)
    stored_job = session.get(ExtractionJob, extraction_job.id)
    stored_candidate = session.get(ExtractionCandidate, candidate.id)
    stored_relationship = session.get(Relationship, relationship.id)

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


def test_campaign_name_must_be_unique_per_owner(session: Session) -> None:
    owner = Owner(email="gm@example.com")
    session.add(owner)
    session.flush()

    session.add_all(
        [
            Campaign(owner_id=owner.id, name="Shadows of Glass"),
            Campaign(owner_id=owner.id, name="Shadows of Glass"),
        ]
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_session_note_requires_number_or_label(session: Session) -> None:
    owner = Owner(email="gm@example.com")
    campaign = Campaign(owner=owner, name="Shadows of Glass")
    session.add_all([owner, campaign])
    session.flush()

    session.add(SessionNote(campaign_id=campaign.id))

    with pytest.raises(IntegrityError):
        session.commit()


def test_session_number_must_be_unique_within_campaign(session: Session) -> None:
    owner = Owner(email="gm@example.com")
    campaign = Campaign(owner=owner, name="Shadows of Glass")
    session.add_all([owner, campaign])
    session.flush()

    session.add_all(
        [
            SessionNote(campaign_id=campaign.id, session_number=7),
            SessionNote(campaign_id=campaign.id, session_number=7, session_label="Seven again"),
        ]
    )

    with pytest.raises(IntegrityError):
        session.commit()
