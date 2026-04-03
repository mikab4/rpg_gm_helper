import httpx
import pytest

from app.config import Settings

TEST_DATABASE_URL = "postgresql+psycopg://test:test@localhost:5432/test_db"


@pytest.mark.anyio
async def test_healthcheck_returns_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    from app.main import create_app

    settings = Settings(_env_file=None)

    transport = httpx.ASGITransport(app=create_app(settings))

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_healthcheck_exposes_named_response_model_in_openapi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    from app.main import create_app

    settings = Settings(_env_file=None)

    transport = httpx.ASGITransport(app=create_app(settings))

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert (
        schema["paths"]["/api/health"]["get"]["responses"]["200"]["content"]["application/json"][
            "schema"
        ]["$ref"]
        == "#/components/schemas/HealthResponse"
    )


@pytest.mark.anyio
async def test_healthcheck_allows_frontend_origin_from_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("BACKEND_CORS_ALLOWED_ORIGINS", "http://localhost:5173")
    from app.main import create_app

    settings = Settings(_env_file=None)

    transport = httpx.ASGITransport(app=create_app(settings))

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
