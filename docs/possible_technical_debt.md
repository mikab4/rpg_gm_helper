# Possible Technical Debt

## App-managed database wiring

Current recommendation for the reviewed import-time DB issue was to remove module-level globals and keep explicit factories in `backend/app/db.py`.

A stronger long-term alternative is to create the SQLAlchemy engine during app bootstrap, store it on FastAPI app state, and expose sessions through a FastAPI dependency.

Why this may be worth doing later:
- It fits the app-factory direction better than process-global engine state.
- It makes per-app-instance DB wiring more explicit for tests and future runtime setup.
- It gives a cleaner place to manage engine lifecycle and disposal once DB-backed routes are added.

Why it was deferred now:
- Nothing in the scaffold currently consumes the database layer.
- Adding app-state and dependency wiring now would be extra abstraction before there is a real DB call path to justify it.
- The explicit factory approach already removes the current brittleness without introducing more lifecycle machinery.

## Frontend API schema validation

Current recommendation for the reviewed frontend API client issue was to keep a thin shared fetch helper that returns `unknown` and require endpoint-specific parsing, starting with the health endpoint.

A stronger long-term alternative is to introduce a schema validation library such as Zod at the network boundary and define explicit response schemas for API contracts.

Why this may be worth doing later:
- It would provide runtime validation and inferred TypeScript types from the same source.
- It would scale better once the frontend starts consuming multiple CRUD and search endpoints.
- It would make backend/frontend drift fail in a more standardized and inspectable way.

Why it was deferred now:
- The scaffold currently has only one real response contract.
- A schema library would add dependency and abstraction overhead before there is enough API surface to justify it.
- Endpoint-local parsing already removes the misleading unchecked cast without committing the project to a validation framework yet.
