from __future__ import annotations

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from alembic import command
from app.config import get_settings
from app.models import (
    Campaign,
    Entity,
    ExtractionCandidate,
    ExtractionJob,
    Owner,
    Relationship,
)
from app.models.session_note import SessionNote
from app.models.source_document import SourceDocument
from tests.pg_test_support import (
    build_alembic_config,
    create_test_engine,
    load_test_settings,
    reset_public_schema,
)

EXPECTED_TABLES = {
    "alembic_version",
    "owners",
    "campaigns",
    "session_notes",
    "source_documents",
    "extraction_jobs",
    "extraction_candidates",
    "entities",
    "entity_relationships",
}


def test_alembic_upgrade_head_creates_expected_tables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = load_test_settings()
    engine = create_test_engine(settings)

    reset_public_schema(engine)

    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    get_settings.cache_clear()

    alembic_config = build_alembic_config()
    upgraded = False

    try:
        command.upgrade(alembic_config, "head")
        upgraded = True

        inspector = inspect(engine)
        assert EXPECTED_TABLES.issubset(set(inspector.get_table_names()))
    finally:
        if upgraded:
            command.downgrade(alembic_config, "base")
        get_settings.cache_clear()
        engine.dispose()


def test_alembic_migration_rejects_cross_campaign_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = load_test_settings()
    engine = create_test_engine(settings)

    reset_public_schema(engine)

    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    get_settings.cache_clear()

    alembic_config = build_alembic_config()
    upgraded = False

    try:
        command.upgrade(alembic_config, "head")
        upgraded = True

        with Session(engine) as session:
            owner = Owner(email="gm@example.com")
            campaign_a = Campaign(owner=owner, name="Campaign A")
            campaign_b = Campaign(owner=owner, name="Campaign B")
            note_b = SessionNote(campaign=campaign_b, session_number=1)
            document_b = SourceDocument(
                campaign=campaign_b,
                session_note=note_b,
                truth_status="canonical",
                raw_text="Document in campaign B",
            )
            job_b = ExtractionJob(
                campaign=campaign_b,
                source_document=document_b,
                status="completed",
                extractor_kind="rules",
            )
            entity_b = Entity(campaign=campaign_b, type="npc", name="Entity B")

            session.add_all([owner, campaign_a, campaign_b, note_b, document_b, job_b, entity_b])
            session.commit()

            invalid_document = SourceDocument(
                campaign=campaign_a,
                session_note_id=note_b.id,
                truth_status="canonical",
                raw_text="Claims campaign A while pointing at campaign B note",
            )
            session.add(invalid_document)
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()

            valid_document_a = SourceDocument(
                campaign=campaign_a,
                truth_status="canonical",
                raw_text="Document in campaign A",
            )
            session.add(valid_document_a)
            session.commit()

            invalid_job = ExtractionJob(
                campaign=campaign_a,
                source_document_id=document_b.id,
                status="pending",
                extractor_kind="rules",
            )
            session.add(invalid_job)
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()

            job_a = ExtractionJob(
                campaign=campaign_a,
                source_document=valid_document_a,
                status="pending",
                extractor_kind="rules",
            )
            session.add(job_a)
            session.commit()

            invalid_candidate = ExtractionCandidate(
                campaign=campaign_a,
                extraction_job_id=job_b.id,
                candidate_type="entity",
                payload={"name": "Mismatch"},
                status="pending",
            )
            session.add(invalid_candidate)
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()

            entity_a = Entity(campaign=campaign_a, type="npc", name="Entity A")
            session.add(entity_a)
            session.commit()

            invalid_relationship = Relationship(
                campaign=campaign_a,
                source_entity=entity_a,
                target_entity_id=entity_b.id,
                relationship_type="knows",
            )
            session.add(invalid_relationship)
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()
    finally:
        if upgraded:
            command.downgrade(alembic_config, "base")
        get_settings.cache_clear()
        engine.dispose()


def test_alembic_migration_restricts_deleting_optional_referenced_parents(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = load_test_settings()
    engine = create_test_engine(settings)

    reset_public_schema(engine)

    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    get_settings.cache_clear()

    alembic_config = build_alembic_config()
    upgraded = False

    try:
        command.upgrade(alembic_config, "head")
        upgraded = True

        with Session(engine) as session:
            owner = Owner(email="gm@example.com")
            campaign = Campaign(owner=owner, name="Campaign A")
            note = SessionNote(campaign=campaign, session_number=1)
            document = SourceDocument(
                campaign=campaign,
                session_note=note,
                truth_status="canonical",
                raw_text="Document linked to a session",
            )
            entity = Entity(
                campaign=campaign,
                type="npc",
                name="Entity A",
                source_document=document,
            )
            relationship = Relationship(
                campaign=campaign,
                source_entity=entity,
                target_entity=entity,
                relationship_type="self_ref",
                source_document=document,
            )

            session.add_all([owner, campaign, note, document, entity, relationship])
            session.commit()

            session.delete(note)
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()

            session.delete(document)
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()
    finally:
        if upgraded:
            command.downgrade(alembic_config, "base")
        get_settings.cache_clear()
        engine.dispose()
