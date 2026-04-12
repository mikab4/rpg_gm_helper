from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alembic import command
from app.api.router import api_router
from app.config import Settings, get_settings


def build_alembic_config(settings: Settings) -> Config:
    alembic_ini_path = Path(__file__).resolve().parent.parent / "alembic.ini"
    alembic_config = Config(str(alembic_ini_path))
    alembic_config.set_main_option("sqlalchemy.url", settings.database_url)
    return alembic_config


def apply_pending_migrations(settings: Settings) -> None:
    alembic_config = build_alembic_config(settings)
    command.upgrade(alembic_config, "head")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def app_lifespan(_app: FastAPI):
        if settings.auto_apply_migrations:
            apply_pending_migrations(settings)
        yield

    app = FastAPI(title=settings.app_name, lifespan=app_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_prefix)
    app.state.settings = settings
    return app


app = create_app()
