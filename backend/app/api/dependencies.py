from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.db import get_db_session_factory


def get_db_session() -> Iterator[Session]:
    db_session_factory = get_db_session_factory()
    with db_session_factory() as db_session:
        yield db_session
