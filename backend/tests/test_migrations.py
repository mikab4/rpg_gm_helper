from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from alembic import command
from app.config import Settings, get_settings
from app.models import Campaign, Entity, ExtractionCandidate, ExtractionJob, Owner, Relationship
from app.models.relationship_type_definition import RelationshipTypeDefinition
from app.models.session_note import SessionNote
from app.models.source_document import SourceDocument
from tests.pg_test_support import (
    build_alembic_config,
    create_test_engine,
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
    "relationship_type_definitions",
}


@contextmanager
def upgraded_engine(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> Iterator[Engine]:
    settings = postgres_test_settings
    engine = create_test_engine(settings)

    reset_public_schema(engine)
    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    get_settings.cache_clear()

    alembic_config = build_alembic_config()
    upgraded = False

    try:
        command.upgrade(alembic_config, "head")
        upgraded = True
        yield engine
    finally:
        if upgraded:
            command.downgrade(alembic_config, "base")
        get_settings.cache_clear()
        engine.dispose()


def test_alembic_upgrade_head_creates_expected_tables(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> None:
    with upgraded_engine(monkeypatch, postgres_test_settings) as engine:
        inspector = inspect(engine)
        relationship_columns = {
            column["name"] for column in inspector.get_columns("entity_relationships")
        }

        assert EXPECTED_TABLES.issubset(set(inspector.get_table_names()))
        assert {"lifecycle_status", "visibility_status", "certainty_status"}.issubset(
            relationship_columns
        )


def test_source_document_rejects_session_note_from_another_campaign(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> None:
    with upgraded_engine(monkeypatch, postgres_test_settings) as engine:
        with Session(engine) as session:
            owner = Owner(email="gm@example.com")
            campaign_a = Campaign(owner=owner, name="Campaign A")
            campaign_b = Campaign(owner=owner, name="Campaign B")
            note_b = SessionNote(campaign=campaign_b, session_number=1)

            session.add_all([owner, campaign_a, campaign_b, note_b])
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


def test_extraction_job_rejects_source_document_from_another_campaign(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> None:
    with upgraded_engine(monkeypatch, postgres_test_settings) as engine:
        with Session(engine) as session:
            owner = Owner(email="gm@example.com")
            campaign_a = Campaign(owner=owner, name="Campaign A")
            campaign_b = Campaign(owner=owner, name="Campaign B")
            document_a = SourceDocument(
                campaign=campaign_a,
                truth_status="canonical",
                raw_text="Document in campaign A",
            )
            document_b = SourceDocument(
                campaign=campaign_b,
                truth_status="canonical",
                raw_text="Document in campaign B",
            )

            session.add_all([owner, campaign_a, campaign_b, document_a, document_b])
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


def test_extraction_candidate_rejects_job_from_another_campaign(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> None:
    with upgraded_engine(monkeypatch, postgres_test_settings) as engine:
        with Session(engine) as session:
            owner = Owner(email="gm@example.com")
            campaign_a = Campaign(owner=owner, name="Campaign A")
            campaign_b = Campaign(owner=owner, name="Campaign B")
            document_a = SourceDocument(
                campaign=campaign_a,
                truth_status="canonical",
                raw_text="Document in campaign A",
            )
            document_b = SourceDocument(
                campaign=campaign_b,
                truth_status="canonical",
                raw_text="Document in campaign B",
            )
            job_b = ExtractionJob(
                campaign=campaign_b,
                source_document=document_b,
                status="completed",
                extractor_kind="rules",
            )

            session.add_all([owner, campaign_a, campaign_b, document_a, document_b, job_b])
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


def test_relationship_rejects_target_entity_from_another_campaign(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> None:
    with upgraded_engine(monkeypatch, postgres_test_settings) as engine:
        with Session(engine) as session:
            owner = Owner(email="gm@example.com")
            campaign_a = Campaign(owner=owner, name="Campaign A")
            campaign_b = Campaign(owner=owner, name="Campaign B")
            source_entity = Entity(campaign=campaign_a, type="npc", name="Entity A")
            foreign_target_entity = Entity(campaign=campaign_b, type="npc", name="Entity B")

            session.add_all([owner, campaign_a, campaign_b, source_entity, foreign_target_entity])
            session.commit()

            invalid_relationship = Relationship(
                campaign=campaign_a,
                source_entity=source_entity,
                target_entity_id=foreign_target_entity.id,
                relationship_type="knows",
            )
            session.add(invalid_relationship)

            with pytest.raises(IntegrityError):
                session.commit()

            session.rollback()


def test_alembic_migration_rejects_invalid_relationship_type_direction_labels(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> None:
    with upgraded_engine(monkeypatch, postgres_test_settings) as engine:
        with Session(engine) as session:
            owner = Owner(email="gm@example.com")
            campaign = Campaign(owner=owner, name="Campaign A")
            session.add_all([owner, campaign])
            session.commit()

            invalid_type = RelationshipTypeDefinition(
                campaign=campaign,
                key="bodyguard_of",
                label="bodyguard of",
                family="social",
                reverse_label=None,
                is_symmetric=False,
                allowed_source_types=["person"],
                allowed_target_types=["person"],
            )
            session.add(invalid_type)

            with pytest.raises(IntegrityError):
                session.commit()

            session.rollback()


def test_session_note_delete_is_restricted_when_source_document_references_it(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> None:
    with upgraded_engine(monkeypatch, postgres_test_settings) as engine:
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


def test_source_document_delete_is_restricted_when_records_reference_it(
    monkeypatch: pytest.MonkeyPatch,
    postgres_test_settings: Settings,
) -> None:
    with upgraded_engine(monkeypatch, postgres_test_settings) as engine:
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

            session.delete(document)

            with pytest.raises(IntegrityError):
                session.commit()

            session.rollback()
