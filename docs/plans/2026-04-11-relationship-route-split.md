# Relationship Route Split Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split the relationship API routes into separate modules for relationship types and relationships without changing API behavior.

**Architecture:** Keep the existing services and schemas unchanged. Move relationship type endpoints into a dedicated route module, leave relationship CRUD in its own route module, and register the two routers separately in the API router with separate tags.

**Tech Stack:** FastAPI, pytest, Ruff

---

### Task 1: Add a router registration test

**Files:**
- Modify: `backend/tests/test_api_router.py`

**Step 1: Write the failing test**

Add a test that inspects `api_router.routes` and asserts:
- `GET /relationship-types` is tagged under `relationship-types`
- `POST /campaigns/{campaign_id}/relationships` is tagged under `relationships`

**Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/test_api_router.py -q`

Expected: FAIL because both resources are currently included through the same router tag.

**Step 3: Write minimal implementation**

Split the route modules and update `backend/app/api/router.py` includes.

**Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_api_router.py -q`

Expected: PASS

### Task 2: Split the route modules

**Files:**
- Create: `backend/app/api/routes/relationship_types.py`
- Modify: `backend/app/api/routes/relationships.py`
- Modify: `backend/app/api/router.py`

**Step 1: Move relationship type endpoints**

Copy the relationship type endpoint handlers and imports into the new route module.

**Step 2: Remove moved endpoints from `relationships.py`**

Keep only relationship CRUD and related imports there.

**Step 3: Register routers separately**

Update `api/router.py` to include:
- `relationship_types_router` with tag `relationship-types`
- `relationships_router` with tag `relationships`

**Step 4: Re-run the targeted router test**

Run: `./.venv/bin/python -m pytest tests/test_api_router.py -q`

Expected: PASS

### Task 3: Verify no route behavior regressions

**Files:**
- Existing tests only

**Step 1: Run relationship API tests**

Run: `./.venv/bin/python -m pytest tests/test_relationships_api.py -q`

Expected: PASS

**Step 2: Run lint**

Run: `./.venv/bin/python -m ruff check app/api/router.py app/api/routes/relationship_types.py app/api/routes/relationships.py tests/test_api_router.py tests/test_relationships_api.py`

Expected: PASS
