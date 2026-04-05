from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models import Base
from app.models.campaign import Campaign
from app.models.owner import Owner


@contextmanager
def patched_jsonb_defaults() -> Iterator[None]:
    patched_columns: list[tuple[Any, Any]] = []
    for metadata_table in Base.metadata.tables.values():
        for table_column in metadata_table.columns:
            column_server_default = table_column.server_default
            if column_server_default is None:
                continue
            if getattr(column_server_default.arg, "text", None) != "'{}'::jsonb":
                continue
            patched_columns.append((table_column, column_server_default))
            table_column.server_default = None

    try:
        yield
    finally:
        for table_column, column_server_default in patched_columns:
            table_column.server_default = column_server_default


@pytest.fixture
def sqlite_engine(tmp_path: Path) -> Iterator[Engine]:
    with patched_jsonb_defaults():
        database_path = tmp_path / "test.db"
        sqlite_db_engine = create_engine(
            f"sqlite+pysqlite:///{database_path}",
            future=True,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(sqlite_db_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection: Any, _connection_record: Any) -> None:
            dbapi_connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(sqlite_db_engine)

        try:
            yield sqlite_db_engine
        finally:
            Base.metadata.drop_all(sqlite_db_engine)


@pytest.fixture
def db_session(sqlite_engine: Engine) -> Iterator[Session]:
    with Session(sqlite_engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
def test_owner(db_session: Session) -> Owner:
    stored_owner = Owner(
        email="gm@example.com",
        display_name="Local GM",
    )
    db_session.add(stored_owner)
    db_session.commit()
    db_session.refresh(stored_owner)
    return stored_owner


@pytest.fixture
def test_campaign(db_session: Session, test_owner: Owner) -> Campaign:
    stored_campaign = Campaign(
        owner_id=test_owner.id,
        name="Shadows of Glass",
        description="Urban intrigue campaign",
    )
    db_session.add(stored_campaign)
    db_session.commit()
    db_session.refresh(stored_campaign)
    return stored_campaign
