# AGENTS.md

## Project Purpose

RPG GM Helper is a single-user, local-first tool for tabletop RPG Game Masters. The first milestone focuses on:
- storing campaign data in a structured way
- ingesting session notes or other free text
- extracting candidate entities and relationships from text
- requiring human review before extracted data becomes canonical
- searching across entities and notes
- optionally exporting approved entities to Kanka

This repository is intentionally being built as a foundation for later work on semantic search, model-assisted extraction, and training-oriented workflows.

## Source Of Truth

Before making product or architecture changes, read:
- `docs/plans/2026-03-31-rpg-gm-helper-v1.md`
- `docs/plans/2026-03-31-rpg-gm-helper-v1-reasoning.md`
- `README.md`

If a proposed change conflicts with those documents, call it out explicitly instead of silently diverging.

## Architecture Rules

- Prefer a modular monolith over microservices.
- Keep the backend in Python with FastAPI.
- Keep PostgreSQL as the primary and only datastore in v1.
- Keep the frontend in React with TypeScript.
- Treat Kanka as an optional export adapter, not the source of truth.
- Keep extraction and search behind internal service boundaries so future semantic search or model-backed extraction can be added cleanly.
- Preserve provenance for extracted entities and relationships.
- Store raw source text so extraction can be rerun later.

## V1 Scope

In scope:
- campaign CRUD
- entity CRUD
- relationship CRUD
- session note CRUD
- source document storage
- extraction jobs and candidate review
- PostgreSQL full-text search
- optional Kanka export

Out of scope for v1 unless explicitly requested:
- multi-user auth
- permissions
- semantic or vector search
- model training pipelines
- Redis or queue infrastructure
- a second database
- bidirectional Kanka sync
- microservices

## Data Modeling Guidance

- Use one generic `Entity` model in v1 rather than separate tables for each RPG concept.
- Use explicit `campaign_id` on campaign-owned resources.
- Reserve room for future auth by keeping an owner or tenant placeholder in major tables.
- Use JSONB only for flexible metadata, not as a substitute for the relational schema.
- Do not use external system IDs such as Kanka IDs as canonical internal identity.

## Implementation Guidance

- Build the smallest working slice that supports the demo flow.
- Prefer deterministic, testable behavior over ambitious automation.
- Use a rules-first extraction implementation for v1, with a clean interface for a future LLM-backed extractor.
- Start with pasted text support before adding more complex upload handling if time is tight.
- Prefer boring, debuggable solutions when tradeoffs are unclear.

## Testing Expectations

At minimum, cover:
- CRUD flows for core records
- extraction candidate generation
- candidate approval and rejection
- provenance preservation
- search behavior
- campaign ownership validation
- Kanka export payload transformation

Use sample notes under `docs/sample-notes/` for repeatable tests and demos.

## Python Workflow Rules

- Use `uv` as the Python package and environment manager for this repository.
- Use standard GIL-enabled CPython 3.14 for this project.
- Do not use the free-threaded Python build unless explicitly requested for a focused experiment.
- Do not introduce Poetry configuration unless explicitly requested.
- Prefer `uv sync` to create or update the project environment.
- Prefer `uv run <command>` for project commands such as tests, linters, Alembic, and Uvicorn.
- For any change to Python code, run `ruff check` before claiming the work is complete.
- If Python files were reformatted or newly created, also run `ruff format`.
- Treat `ruff` findings as blockers unless there is a documented reason not to.
- Prefer code that passes `ruff` cleanly without adding suppressions unless a suppression is justified.

## Documentation Expectations

When changing architecture, scope, or major workflows:
- update `README.md` if the user-facing setup or project description changes
- update the relevant file under `docs/plans/` if the intended design changes
- add or update demo/sample notes when they help verify new behavior

## Working Style

- Be explicit about assumptions that affect architecture or schema.
- Push back on premature complexity.
- Surface a simpler alternative when proposing a heavier design.
- Do not introduce new infrastructure just to make the project look more advanced.
- Optimize for a working product that can grow, not for maximal abstraction.
