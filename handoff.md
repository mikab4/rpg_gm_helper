# Handoff

## Workspace

- Repo root: `/home/mikab4/projects/rpg_gm_helper`
- Active worktree: `/home/mikab4/projects/rpg_gm_helper/.worktrees/relationship_sementics_v1`
- Branch: `relationship_sementics_v1`

## What Was Implemented

### Relationship semantics v1 backend

Added:
- campaign-scoped custom relationship type definitions
- relationship CRUD routes
- relationship type catalog routes
- relationship assertion state fields:
  - `lifecycle_status`
  - `visibility_status`
  - `certainty_status`
- built-in relationship catalog with validation metadata
- campaign custom relationship types with medium editability:
  - label/reverse label editable anytime
  - semantic fields locked after first use

Main files:
- `backend/app/api/routes/relationships.py`
- `backend/app/services/relationship_service.py`
- `backend/app/services/relationship_type_service.py`
- `backend/app/services/relationship_catalog.py`
- `backend/app/models/relationship.py`
- `backend/app/models/relationship_type_definition.py`
- `backend/alembic/versions/20260410_0002_relationship_semantics_v1.py`

### Docs added

- `docs/plans/2026-04-10-relationship-semantics-v1.md`
- `docs/plans/2026-04-10-relationship-semantics-v1-reasoning.md`

## Follow-up Change Done After Initial Implementation

The user requested that controlled vocabularies in Python use `StrEnum` instead of hardcoded string sets.

Added shared enum definitions in:
- `backend/app/enums.py`

Current schema/API usage now uses `StrEnum` for:
- `EntityType`
- `RelationshipFamily`
- `RelationshipLifecycleStatus`
- `RelationshipVisibilityStatus`
- `RelationshipCertaintyStatus`
- `HealthStatus`

Also defined for future/current backend use:
- `SourceDocumentTruthStatus`
- `ExtractionJobStatus`
- `ExtractorKind`
- `ExtractionCandidateType`
- `ExtractionCandidateStatus`

Main enum-related files changed:
- `backend/app/schemas/entities.py`
- `backend/app/schemas/entity_types.py`
- `backend/app/schemas/relationship_types.py`
- `backend/app/schemas/relationships.py`
- `backend/app/api/models.py`
- `backend/app/api/routes/health.py`
- `backend/app/services/relationship_catalog.py`
- `backend/app/services/relationship_service.py`

## Current Behavior / Decisions

- DB columns remain `text`, not DB enums.
- Python code should prefer `StrEnum` for controlled vocabularies.
- One generic `Relationship` model remains the storage design.
- No inferred relationships are implemented.
- `leader_of` is organization-only.
- `governs` is the territorial political authority relation.
- `spouse_of` is in `romance`, not `family`.
- `located_in` is the location containment relation.
- `confidence` remains provenance/scoring context, not truth semantics.

## Verification Already Run

In `backend/`:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check
```

Latest results:
- `60 passed, 10 skipped`
- `ruff check` passed

## Likely Next Steps

Possible next session targets:
- continue enum adoption into model annotations for other controlled string fields if desired
  - `SourceDocument.truth_status`
  - `ExtractionJob.status`
  - `ExtractionJob.extractor_kind`
  - `ExtractionCandidate.candidate_type`
  - `ExtractionCandidate.status`
- expose enum usage more consistently in future document/extraction schemas once those APIs are built
- start frontend/backend integration for step 7 relationship screens and typed client support

## Notes

- The branch name intentionally matches the user’s spelling: `relationship_sementics_v1`.
- There are unrelated untracked files in the main repo root workspace, which is why this work was done in the worktree.
