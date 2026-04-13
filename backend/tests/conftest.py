from __future__ import annotations

import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import anyio.to_thread
import fastapi.concurrency
import fastapi.dependencies.utils
import fastapi.routing
import httpx
import pytest
import starlette.concurrency
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_db_session
from app.config import Settings
from app.models import Base
from app.models.campaign import Campaign
from app.models.owner import Owner
from tests.pg_test_support import (
    PostgresTestContainer,
    ensure_postgres_test_container,
    load_test_settings,
    remove_postgres_test_container,
)


@pytest.fixture
def sync_api_test_runtime_shim(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    # In this sandbox, the normal AnyIO-backed threadpool path hangs for sync
    # FastAPI handlers under in-process ASGI tests. Inline execution keeps the
    # HTTP request/response stack, dependency injection, and validation paths in
    # process without changing production code.
    async def inline_run_in_threadpool(func, *args, **kwargs):
        return func(*args, **kwargs)

    async def inline_run_sync(
        func,
        *args,
        abandon_on_cancel: bool = False,
        cancellable=None,
        limiter=None,
    ):
        del abandon_on_cancel, cancellable, limiter
        return func(*args)

    monkeypatch.setattr(starlette.concurrency, "run_in_threadpool", inline_run_in_threadpool)
    monkeypatch.setattr(fastapi.routing, "run_in_threadpool", inline_run_in_threadpool)
    monkeypatch.setattr(
        fastapi.dependencies.utils,
        "run_in_threadpool",
        inline_run_in_threadpool,
    )
    monkeypatch.setattr(fastapi.concurrency, "run_in_threadpool", inline_run_in_threadpool)
    monkeypatch.setattr(anyio.to_thread, "run_sync", inline_run_sync)
    yield


@contextmanager
def patched_jsonb_defaults() -> Iterator[None]:
    patched_columns: list[tuple[Any, Any]] = []
    jsonb_defaults = {"'{}'::jsonb", "'[]'::jsonb"}
    for metadata_table in Base.metadata.tables.values():
        for table_column in metadata_table.columns:
            column_server_default = table_column.server_default
            if column_server_default is None:
                continue
            if getattr(column_server_default.arg, "text", None) not in jsonb_defaults:
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
def db_session_factory(sqlite_engine: Engine):
    return sessionmaker(bind=sqlite_engine, expire_on_commit=False, future=True)


@pytest.fixture
def test_owner(db_session_factory) -> Owner:
    with db_session_factory() as db_session:
        stored_owner = Owner(
            email="gm@example.com",
            display_name="Local GM",
        )
        db_session.add(stored_owner)
        db_session.commit()
        db_session.refresh(stored_owner)
        db_session.expunge(stored_owner)
        return stored_owner


@pytest.fixture
def test_campaign(db_session_factory, test_owner: Owner) -> Campaign:
    with db_session_factory() as db_session:
        stored_campaign = Campaign(
            owner_id=test_owner.id,
            name="Shadows of Glass",
            description="Urban intrigue campaign",
        )
        db_session.add(stored_campaign)
        db_session.commit()
        db_session.refresh(stored_campaign)
        db_session.expunge(stored_campaign)
        return stored_campaign


@pytest.fixture
def test_app(sqlite_engine: Engine, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///unused-for-tests.db")

    from app.main import create_app

    app = create_app(
        settings=None,
    )

    def override_get_db_session():
        with Session(sqlite_engine, expire_on_commit=False) as db_session:
            yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def api_client_factory(test_app, sync_api_test_runtime_shim):
    def create_api_client() -> httpx.AsyncClient:
        transport = httpx.ASGITransport(app=test_app)
        return httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            timeout=5.0,
        )

    return create_api_client


@pytest.fixture
def api_request(test_app, sync_api_test_runtime_shim):
    def issue_api_request(method: str, path: str, **kwargs):
        async def send_request():
            transport = httpx.ASGITransport(app=test_app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
                timeout=5.0,
            ) as api_client:
                return await api_client.request(method, path, **kwargs)

        return asyncio.run(send_request())

    return issue_api_request


@pytest.fixture(scope="session")
def postgres_test_container() -> Iterator[PostgresTestContainer]:
    runtime_container = ensure_postgres_test_container()

    try:
        yield runtime_container
    finally:
        remove_postgres_test_container(runtime_container.container_name)


@pytest.fixture(scope="session")
def postgres_test_settings(postgres_test_container: PostgresTestContainer) -> Settings:
    return load_test_settings(runtime_database_url=postgres_test_container.database_url)
