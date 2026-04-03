# Frontend Scaffold Design

**Date:** 2026-04-03

## Goal

Finish the frontend scaffold so it is runnable and visibly connected to the backend in the most basic way, without guessing unfinished CRUD contracts.

## Constraints

- Keep the frontend aligned with the v1 plan in `docs/plans/2026-03-31-rpg-gm-helper-v1.md`.
- Do not invent entity CRUD request or response shapes before the backend exposes them.
- Use a real router so the app structure is navigable now.
- Prove frontend-backend connectivity using the backend surface that actually exists today: `GET /api/health`.

## Options Considered

### Option 1: Real router plus live health check

Add `react-router-dom`, build a shared app shell with navigation, and create a minimal typed API client for the health endpoint. Route placeholders exist for the planned areas, but only the overview page performs a real backend call.

Pros:
- Proves the app runs and connects to the backend now.
- Completes the scaffold structure safely.
- Avoids churn from speculative CRUD types.

Cons:
- Most routed pages are placeholders until backend CRUD work lands.

### Option 2: Real router plus speculative CRUD client

Add router and start defining campaign or entity client contracts now.

Pros:
- Looks more complete on paper.

Cons:
- High risk of rework because the backend only exposes `GET /health`.
- Pushes unstable assumptions into the frontend.

### Option 3: Router only, no live backend call

Add app structure without any fetch path.

Pros:
- Lowest implementation cost.

Cons:
- Fails the stated goal of seeing the frontend and backend connect.

## Recommendation

Choose Option 1.

It is the smallest working slice that demonstrates a real app shell, real routing, and real backend communication. It also respects the project guidance to prefer boring, debuggable solutions and to avoid premature complexity.

## Design

### App Structure

Create a shared shell with a persistent header, navigation, and routed content area. Include routes for:

- `/`
- `/campaigns`
- `/entities`
- `/session-notes`
- `/extraction-review`
- `/search`

The non-overview pages should clearly state that the screen is scaffolded and waiting on backend CRUD or workflow endpoints.

### API Boundary

Create a minimal `src/api` module with:

- a base URL sourced from `VITE_API_BASE_URL`
- a small fetch helper
- a typed `getHealth()` function returning the backend health payload

This is enough to establish the client pattern without freezing broader backend contracts too early.

### Live Connectivity

The overview route should request backend health on load and render one of three states:

- loading
- connected with returned status payload
- unreachable with an actionable error message

This gives an immediate visual signal when the backend is not running or the frontend env is wrong.

### Types

Add only stable types that are already backed by the existing backend response:

- `HealthResponse`

Do not add entity, campaign, or note DTOs yet.

### Testing

Add one frontend test covering the overview page behavior around a successful health fetch. Keep the test surface narrow and avoid adding a large frontend testing stack unless required to support this minimal behavior.

## Trade-Off Summary

This design intentionally stops short of frontend CRUD implementation. That is the simpler alternative to speculative client work, and it is the right boundary while backend CRUD is still in progress.
