from __future__ import annotations

from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command
from app.config import get_settings, load_settings

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
    env_file = Path(__file__).resolve().parent.parent / ".env.test"
    if not env_file.is_file():
        pytest.skip("Create backend/.env.test to run Postgres migration integration tests.")

    settings = load_settings(env_file=env_file)
    engine = create_engine(settings.database_url, future=True)

    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))

    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    get_settings.cache_clear()

    alembic_config = Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
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
