from __future__ import annotations

from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import NullPool

from app.config import Settings, load_settings


def load_test_settings() -> Settings:
    env_file = Path(__file__).resolve().parent.parent / ".env.test"
    if not env_file.is_file():
        pytest.skip("Create backend/.env.test to run Postgres migration integration tests.")

    return load_settings(env_file=env_file)


def build_alembic_config() -> Config:
    return Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))


def create_test_engine(settings: Settings) -> Engine:
    return create_engine(settings.database_url, future=True, poolclass=NullPool)


def reset_public_schema(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
