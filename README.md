# RPG GM Helper

RPG GM Helper is a single-user, local-first tool for Game Masters to store campaign data, ingest free-text notes, extract candidate entities, review them before saving, and search across structured world data and notes.

## Current Status

This repository is in the planning and initialization stage. The implementation direction is documented here:

- [V1 implementation plan](docs/plans/2026-03-31-rpg-gm-helper-v1.md)
- [Plan reasoning and tradeoffs](docs/plans/2026-03-31-rpg-gm-helper-v1-reasoning.md)

## V1 Goal

Build a demoable first version with these capabilities:
- manage campaigns
- create and edit entities and session notes
- paste or upload source text
- extract candidate entities and relationships from notes
- review and approve extracted candidates before persistence
- search entities and notes with PostgreSQL full-text search
- optionally export approved entities to Kanka

## Planned Stack

- Backend: FastAPI
- Database: PostgreSQL
- Frontend: React + TypeScript
- Search: PostgreSQL full-text search
- Extraction: rules-first, with a future optional LLM-backed implementation

## Initial Repository Shape

Planned directories:
- `backend/` for the FastAPI application, models, migrations, and tests
- `frontend/` for the React TypeScript app
- `docs/plans/` for planning documents
- `docs/sample-notes/` for demo and extraction fixture notes

## Deliberately Deferred

These are intentionally out of scope for v1:
- multi-user auth
- semantic or vector search
- model training
- microservices
- Redis and queue infrastructure
- NoSQL persistence
- bidirectional Kanka sync

## Next Steps

1. Scaffold the backend and frontend applications.
2. Define the initial PostgreSQL schema and migrations.
3. Implement campaign, entity, note, and document flows.
4. Build extraction, review, and search workflows.
5. Add optional Kanka export.

## Demo Materials

- [Demo script](docs/demo-script.md)
- [Sample notes](docs/sample-notes/README.md)
