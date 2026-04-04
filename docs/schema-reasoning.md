# Schema Reasoning For V1

This document explains the main schema decisions currently reflected in the v1 planning docs.

## Why The Schema Stays Small

The current milestone is meant to prove the core workflow:

- store campaign data
- ingest text
- extract candidate structure
- require review before canonical persistence
- support later search

The schema should support that workflow without pretending the domain model is already stable. That means preferring boring relational tables with a few flexible `JSONB` fields over subtype tables, dynamic configuration tables, or early infrastructure for future features.

## Why We Use UUID Primary Keys

UUIDs were chosen for all primary keys to keep identifiers stable across future export, sync, and local-first evolution. `BIGINT` would have been simpler in the short term, but UUIDs reduce later migration pressure and are still straightforward for this scale.

## Why `owners` Exists Even Though Auth Is Deferred

The product is still single-user in v1, but the schema keeps an `owners` table so campaigns already have a future auth and tenancy anchor. The current assumption is one seeded local owner row rather than full auth flows.

## Why `session_notes` And `source_documents` Are Separate

There was an important terminology correction during planning:

- `session_notes` represents an actual game session in the campaign timeline
- `source_documents` represents textual evidence or source material

This matters because session notes in RPG play are often incomplete, biased, or subjective. A session is not just a blob of text; it is a real event in the campaign. The text artifacts about that session belong in `source_documents`, optionally linked back to a `session_notes` row.

This model also lets a session have multiple attached documents, such as player notes, GM recap text, or a cleaned-up summary.

## Why `source_documents` Stores Truth Status Instead Of Document Genre

The early idea of `document_kind` was too focused on file category. The more important distinction for this product is whether a source text is treated as:

- canonical
- uncertain
- subjective

That matches the actual tabletop use case better than labels like `session_note` or `reference`, because the workflow depends on whether the text should be treated as reliable world truth or only as evidence that needs interpretation.

## Why Images Are Deferred

The user identified valid future image use cases such as city maps, continent art, or timeline graphics. Those are real source materials, but they are out of scope for the initial schema because Task 3 is centered on text ingestion, extraction, and review. Keeping `source_documents` text-only avoids overloading the first schema with binary or media concerns before there is a concrete v1 need.

## Why Extraction Jobs And Candidates Are Separate

The extraction workflow needs two different concepts:

- a record of each extraction run
- a set of reviewable proposed facts produced by that run

`extraction_jobs` stores run history, extractor kind, status, and completion timing. `extraction_candidates` stores reviewable proposed entities or relationships. This separation preserves rerun history and keeps review state distinct from canonical world data.

## Why Candidates Use One Generic Table

A single `extraction_candidates` table was chosen instead of separate candidate tables for entities and relationships. That keeps the review flow simpler in v1:

- one review queue
- one approval or rejection workflow
- easier evolution of extraction output while the rules-based extractor is still changing

`candidate_type` plus a structured `payload` is enough for the first milestone.

## Why `entities` Stays Generic

The current product needs one canonical record model for people, places, factions, items, and other world concepts. Separate subtype tables would be more rigid and would slow iteration while the domain model is still being learned. A generic `entities` table with:

- `type`
- `name`
- `summary`
- `metadata`

is the right compromise for v1.

## Why Relationships Stay As Directed Rows

Relationships are stored in the `entity_relationships` table as directed assertions using:

- `source_entity_id`
- `target_entity_id`
- `relationship_type`

This supports both one-way relationships like `lives_in` and symmetric semantics like `sibling_of` without duplicating rows. Symmetry and reverse-language handling stay in backend code rather than in extra schema tables for v1.

## Why Controlled Vocabularies Stay In Backend Code

For `entities.type`, `entity_relationships.relationship_type`, and `source_documents.truth_status`, the agreed choice was:

- store plain text in the database
- validate allowed values in backend code

This is less strict than DB constraints or dedicated lookup tables, but it keeps v1 easier to evolve while the vocabulary is still being discovered. The design leaves room to add stricter DB enforcement later if the vocabularies stabilize.

## Why Search Schema Work Is Deferred

The original plan placed PostgreSQL full-text search columns and indexes in Task 3. That is now intentionally deferred. The schema task should focus first on the core canonical and evidence tables. Search-specific vectors and indexes can be added when the search task is implemented, once the final searchable fields are clearer.

## Why Kanka Is Removed From The Initial Schema Plan

Kanka export was deprioritized because it is not central to validating the main product workflow and may never be implemented. Keeping it in the initial schema would add tables and assumptions for a feature that is no longer part of the current critical path. The v1 schema now focuses only on campaign data, source text, extraction, review, and canonical persistence.
