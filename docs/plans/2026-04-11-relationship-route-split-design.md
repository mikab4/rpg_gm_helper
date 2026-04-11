# Relationship Route Split Design

## Goal

Split the current mixed relationship API route module into two route modules that match the existing backend service split:

- relationship type catalog and custom type management
- relationship instance CRUD

## Problem

The current [relationships route module](/home/mikab4/projects/rpg_gm_helper/.worktrees/relationship_sementics_v1/backend/app/api/routes/relationships.py) owns endpoints for two distinct resources:

- `relationship-types`
- `relationships`

That made the initial vertical slice faster to land, but it now mixes configuration/catalog endpoints with instance CRUD endpoints and causes both to be included under the same API router tag.

## Chosen Approach

Create two route modules:

- `backend/app/api/routes/relationship_types.py`
- `backend/app/api/routes/relationships.py`

Then update `backend/app/api/router.py` to include them separately with separate tags:

- `relationship-types`
- `relationships`

## Why This Approach

- matches the existing service split between `relationship_type_service` and `relationship_service`
- keeps each route module focused on a single resource
- improves OpenAPI grouping without changing request paths
- keeps the refactor small and boring

## Non-Goals

- no path changes
- no schema changes
- no service behavior changes
- no response shape changes

## Verification

- add a targeted router test to verify the two tags are registered separately
- run the targeted API/router tests
- run `ruff check` on the touched backend files
