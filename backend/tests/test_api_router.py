from __future__ import annotations

from fastapi.routing import APIRoute

from app.api.router import api_router


def test_relationship_routes_are_grouped_under_separate_tags() -> None:
    tagged_paths = {
        (route.path, frozenset(route.methods)): tuple(route.tags)
        for route in api_router.routes
        if isinstance(route, APIRoute)
    }

    assert tagged_paths[("/relationship-types", frozenset({"GET"}))] == ("relationship-types",)
    assert tagged_paths[("/campaigns/{campaign_id}/relationship-types", frozenset({"POST"}))] == (
        "relationship-types",
    )
    assert tagged_paths[("/campaigns/{campaign_id}/relationships", frozenset({"GET"}))] == (
        "relationships",
    )
    assert tagged_paths[("/campaigns/{campaign_id}/relationships", frozenset({"POST"}))] == (
        "relationships",
    )
    assert tagged_paths[("/compatibility/entity-types", frozenset({"GET"}))] == ("compatibility",)
    assert tagged_paths[("/compatibility/entity-types/migrate", frozenset({"POST"}))] == (
        "compatibility",
    )
