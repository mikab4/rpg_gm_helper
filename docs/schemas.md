# RPG GM Helper V1 Schemas

This document captures the current agreed v1 database schema direction in plain language for quick reference.

## Conventions

- Use `UUID` primary keys on all tables.
- Use `created_at timestamptz not null` and `updated_at timestamptz not null` on long-lived records.
- Keep flexible fields in `JSONB`, but do not use `JSONB` instead of obvious relational columns.
- Validate controlled text fields in backend code rather than with PostgreSQL enums or DB check constraints in v1.

## Owners

- `id UUID PK`
- `email text nullable`
- `display_name text nullable`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Notes:
- `owners` exists as a future-auth placeholder.
- v1 assumes one seeded local owner.

## Campaigns

- `id UUID PK`
- `owner_id UUID not null FK -> owners.id`
- `name text not null`
- `description text nullable`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Constraints:
- Unique `(owner_id, name)`

## Session Notes

- `id UUID PK`
- `campaign_id UUID not null FK -> campaigns.id`
- `session_number integer nullable`
- `session_label text nullable`
- `played_on date nullable`
- `summary text nullable`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Constraints:
- At least one of `session_number` or `session_label` must be present.
- `session_number` is unique per campaign when present.

Meaning:
- `session_notes` represents an actual play session in the campaign timeline.
- It does not store the raw source text itself.

## Source Documents

- `id UUID PK`
- `campaign_id UUID not null FK -> campaigns.id`
- `session_note_id UUID nullable FK -> session_notes.id`
- `title text nullable`
- `truth_status text not null`
- `raw_text text not null`
- `metadata JSONB not null default '{}'`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Allowed `truth_status` values in backend code:
- `canonical`
- `uncertain`
- `subjective`

Meaning:
- `source_documents` stores textual evidence or source material only.
- A document may be linked to a session note, but world material can exist without a session link.
- Images and other binary assets are explicitly deferred.

## Extraction Jobs

- `id UUID PK`
- `campaign_id UUID not null FK -> campaigns.id`
- `source_document_id UUID not null FK -> source_documents.id`
- `status text not null`
- `extractor_kind text not null`
- `error_message text nullable`
- `created_at timestamptz not null`
- `completed_at timestamptz nullable`

Allowed values in backend code:
- `status`: `pending`, `running`, `completed`, `failed`
- `extractor_kind`: `rules`

Meaning:
- One extraction job represents one extraction run over one source document.
- Keep this lightweight in v1; `started_at` and generic `updated_at` were intentionally deferred.

## Extraction Candidates

- `id UUID PK`
- `campaign_id UUID not null FK -> campaigns.id`
- `extraction_job_id UUID not null FK -> extraction_jobs.id`
- `candidate_type text not null`
- `payload JSONB not null`
- `status text not null`
- `review_notes text nullable`
- `provenance_excerpt text nullable`
- `provenance_data JSONB not null default '{}'`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Allowed values in backend code:
- `candidate_type`: `entity`, `relationship`
- `status`: `pending`, `approved`, `rejected`

Meaning:
- Candidates are reviewable proposals, not canonical facts.
- Editing during review changes the candidate payload before approval; there is no separate `edited` status.

## Entities

- `id UUID PK`
- `campaign_id UUID not null FK -> campaigns.id`
- `type text not null`
- `name text not null`
- `summary text nullable`
- `metadata JSONB not null default '{}'`
- `source_document_id UUID nullable FK -> source_documents.id`
- `provenance_excerpt text nullable`
- `provenance_data JSONB not null default '{}'`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Meaning:
- `entities` stores canonical approved world records.
- `type` stays generic in v1 and is validated in backend code.
- No DB uniqueness is enforced on entity names in v1.

## Relationships

- `id UUID PK`
- `campaign_id UUID not null FK -> campaigns.id`
- `source_entity_id UUID not null FK -> entities.id`
- `target_entity_id UUID not null FK -> entities.id`
- `relationship_type text not null`
- `notes text nullable`
- `confidence numeric nullable`
- `source_document_id UUID nullable FK -> source_documents.id`
- `provenance_excerpt text nullable`
- `provenance_data JSONB not null default '{}'`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Meaning:
- A relationship row is stored as a directed assertion.
- Symmetric behavior, allowed relationship types, and reverse labels are backend semantics, not separate schema tables in v1.
- Canonical relationships may still keep optional confidence.

## Explicitly Deferred From The Initial Schema

- `kanka_export_jobs`
- PostgreSQL search vector columns and search indexes
- image or binary asset storage
- DB check constraints for controlled text vocabularies
- a `relationship_types` table
