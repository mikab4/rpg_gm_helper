from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.models.base import Base

__all__ = ["Base", "get_engine", "get_session_factory"]


def get_engine(settings: Settings | None = None):
    settings = settings or get_settings()
    return create_engine(settings.database_url, future=True)


def get_session_factory(settings: Settings | None = None):
    return sessionmaker(
        bind=get_engine(settings),
        autoflush=False,
        autocommit=False,
        future=True,
    )
