from __future__ import annotations

from app.models.owner import Owner


def test_get_default_owner_returns_existing_owner(
    api_request,
    test_owner: Owner,
) -> None:
    response = api_request("GET", "/api/owners/default")

    assert response.status_code == 200
    assert response.json()["id"] == str(test_owner.id)
    assert response.json()["email"] == "gm@example.com"
    assert response.json()["display_name"] == "Local GM"


def test_get_default_owner_creates_local_owner_when_none_exists(
    api_request,
    db_session_factory,
) -> None:
    response = api_request("GET", "/api/owners/default")

    assert response.status_code == 200
    response_payload = response.json()
    assert response_payload["email"] == "gm@example.com"
    assert response_payload["display_name"] == "Local GM"

    with db_session_factory() as db_session:
        stored_owners = db_session.query(Owner).all()

    assert len(stored_owners) == 1
    assert str(stored_owners[0].id) == response_payload["id"]
