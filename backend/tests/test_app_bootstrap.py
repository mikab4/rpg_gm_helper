from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import httpx
import pytest

from app.config import Settings

TEST_DATABASE_URL = "postgresql+psycopg://test:test@localhost:5432/test_db"


@pytest.fixture
def app_settings_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., Settings]:
    def build_settings(**overrides: object) -> Settings:
        monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)

        cors_origins = overrides.pop("backend_cors_allowed_origins", None)
        if cors_origins is None:
            monkeypatch.delenv("BACKEND_CORS_ALLOWED_ORIGINS", raising=False)
        else:
            monkeypatch.setenv(
                "BACKEND_CORS_ALLOWED_ORIGINS",
                ",".join(cors_origins),
            )

        auto_apply_migrations = overrides.pop("auto_apply_migrations", None)
        if auto_apply_migrations is None:
            monkeypatch.delenv("AUTO_APPLY_MIGRATIONS", raising=False)
        else:
            monkeypatch.setenv(
                "AUTO_APPLY_MIGRATIONS",
                str(auto_apply_migrations).lower(),
            )

        return Settings(_env_file=None, **overrides)

    return build_settings


@pytest.fixture
def app_client_factory() -> Callable[[Settings], AsyncIterator[httpx.AsyncClient]]:
    @asynccontextmanager
    async def build_client(settings: Settings) -> AsyncIterator[httpx.AsyncClient]:
        from app.main import create_app

        transport = httpx.ASGITransport(app=create_app(settings))
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as api_client:
            yield api_client

    return build_client


@pytest.mark.anyio
async def test_healthcheck_returns_ok(
    app_settings_factory,
    app_client_factory,
) -> None:
    # Arrange
    app_settings = app_settings_factory()

    # Act
    async with app_client_factory(app_settings) as api_client:
        response = await api_client.get("/api/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_healthcheck_allows_frontend_origin_from_settings(
    app_settings_factory,
    app_client_factory,
) -> None:
    # Arrange
    app_settings = app_settings_factory(
        backend_cors_allowed_origins=["http://localhost:5173"],
    )

    # Act
    async with app_client_factory(app_settings) as api_client:
        response = await api_client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

    # Assert
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


@pytest.mark.anyio
async def test_app_startup_runs_pending_migrations_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
    app_settings_factory,
) -> None:
    migrated_settings: list[Settings] = []

    def fake_apply_pending_migrations(settings: Settings) -> None:
        migrated_settings.append(settings)

    app_settings = app_settings_factory(auto_apply_migrations=True)
    from app.main import create_app

    monkeypatch.setattr("app.main.apply_pending_migrations", fake_apply_pending_migrations)
    app = create_app(app_settings)

    async with app.router.lifespan_context(app):
        pass

    assert migrated_settings == [app_settings]


@pytest.mark.anyio
async def test_app_startup_skips_pending_migrations_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
    app_settings_factory,
) -> None:
    migrated_settings: list[Settings] = []

    def fake_apply_pending_migrations(settings: Settings) -> None:
        migrated_settings.append(settings)

    app_settings = app_settings_factory(auto_apply_migrations=False)
    from app.main import create_app

    monkeypatch.setattr("app.main.apply_pending_migrations", fake_apply_pending_migrations)
    app = create_app(app_settings)

    async with app.router.lifespan_context(app):
        pass

    assert migrated_settings == []
