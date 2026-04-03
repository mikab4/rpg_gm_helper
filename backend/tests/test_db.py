import importlib
import sys

import pytest


def test_importing_db_module_does_not_require_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    sys.modules.pop("app.db", None)

    module = importlib.import_module("app.db")

    assert hasattr(module, "get_engine")
