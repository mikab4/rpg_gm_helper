from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import Settings, get_settings

Base = declarative_base()


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
