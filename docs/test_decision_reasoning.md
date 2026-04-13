# Test Decision Reasoning

## Purpose

This document records the testing infrastructure decisions made so far for the backend suite, why they were made, and which fixtures are intended to remain part of the readable test surface.

The main goals behind these decisions are:

- keep tests readable as executable documentation
- make scenario data visible in the test body
- keep heavy infrastructure setup out of individual tests
- preserve real PostgreSQL coverage where SQLite would give false confidence
- reduce manual setup required to run the suite

## Why The Backend Uses Two Test Layers

The backend test suite has two different kinds of database-backed tests:

- SQLite-backed tests for most API, validation, and service behavior
- PostgreSQL-backed tests for migrations and database behavior that depends on real PostgreSQL semantics

This split is intentional.

SQLite is cheap and fast for ordinary request/response and domain behavior tests. It keeps most of the suite lightweight and suitable for frequent local runs.

PostgreSQL is still required for migration and schema-level tests because those tests validate behavior that SQLite does not model faithfully, including Alembic migration execution, PostgreSQL defaults, and constraint behavior. Replacing those tests with SQLite equivalents would reduce confidence while appearing to improve convenience.

## Why PostgreSQL Tests Were Kept Instead Of Removed

The PostgreSQL-backed tests in `backend/tests/test_models.py` and `backend/tests/test_migrations.py` were kept because they are the only tests that prove:

- the Alembic migrations apply cleanly to a real PostgreSQL database
- PostgreSQL constraints actually behave as intended
- the ORM and schema defaults behave correctly under PostgreSQL

Removing those tests would make the suite easier to run, but only by dropping important coverage. The chosen direction was to automate their environment instead of weakening the suite.

## Why PostgreSQL Test Setup Moved To Docker

The earlier approach depended on a developer-managed test database and `.env.test` setup. That created two problems:

- developers had to prepare infrastructure manually before running tests
- PostgreSQL-backed tests skipped too easily when the environment was missing

The chosen fix was a Dockerized PostgreSQL harness managed by the test suite itself.

The backend now provisions a disposable PostgreSQL container for the pytest session and injects the runtime database URL into the PostgreSQL-backed tests. This keeps the real database coverage while moving setup into the test harness rather than into developer memory.

## Why The Docker Harness Is Session-Scoped

The PostgreSQL container is session-scoped instead of per-test or per-module.

That choice was made because:

- one container per session is much faster than provisioning a database repeatedly
- teardown is still simple and explicit
- it matches how this can later run in CI, including GitHub Actions service-container setups
- the PostgreSQL-backed tests already reset schema state explicitly where needed

Per-test containers would increase isolation, but the cost in speed and complexity is not justified by the current suite.

## Why Docker Failures Are Explicit Errors Instead Of Skips

The PostgreSQL-backed tests now fail with explicit setup errors when Docker is unavailable or unusable.

That is intentional. Silent skips would hide broken automation and create false confidence that the suite is healthy. If the repo claims PostgreSQL tests run automatically, then missing Docker access is a broken prerequisite, not a reason to pretend the suite passed.

## Why Test Support Code Has Its Own Tests

The support code in `backend/tests/pg_test_support.py` is project behavior, not framework internals.

It decides:

- how runtime PostgreSQL settings are constructed
- how Docker availability is checked
- how a container is started and torn down
- what error messages developers see when setup is broken

That logic is important enough to deserve focused tests. The goal is not to test pytest or Docker themselves. The goal is to verify our own harness contract so environment failures are deterministic and understandable.

## Why SQLite Still Uses `patched_jsonb_defaults`

`patched_jsonb_defaults` remains in place for SQLite-backed tests.

This is acknowledged as a compromise, but it was deliberately left unchanged in this refactor. Replacing PostgreSQL server defaults with Python-side defaults would change what the suite is exercising and would turn a readability-focused test refactor into a behavior-design change.

The current decision is:

- keep the patch for SQLite test compatibility
- let PostgreSQL-backed tests remain the source of truth for real default behavior
- defer any deeper default-strategy redesign to a separate decision

## Why The Suite Moved To `factory-boy`

The suite previously relied on fixed object fixtures such as `test_owner` and `test_campaign`. Those fixtures were convenient, but they hid scenario setup and forced readers to leave the test file to understand the starting state.

The suite now uses `factory-boy` to create generic, composable factories while keeping the scenario visible in each test.

This was chosen over keeping only hand-written factories because:

- the model set is already large enough that generic factory definitions reduce repeated boilerplate
- `factory-boy` keeps related-object construction consistent across the suite
- the callable pytest fixtures on top of the factories let tests stay explicit about the data that matters

This was also chosen over many named scenario fixtures because named scenario fixtures tend to hide business meaning behind labels like `campaign_with_entities` or `owner_with_overdue_order`.

## Why Factories Are Wrapped In Pytest Fixtures

The suite does not expose raw factory classes directly as the primary test API. Instead, `conftest.py` exposes callable fixtures such as `owner_factory` and `campaign_factory`.

That decision keeps the test surface aligned with the readability rule:

- infrastructure stays in `conftest.py`
- scenario data stays in the test body

The fixture call makes the Arrange step explicit:

```python
owner = owner_factory(email="gm@example.com", display_name="Local GM")
campaign = campaign_factory(owner=owner, name="Iron Vale")
```

This is intentionally more explicit than a fixed fixture, while still shorter and safer than repeating full ORM setup everywhere.

## Why Fixed Scenario Fixtures Were Removed

The old `test_owner` and `test_campaign` fixtures were removed because they created hidden setup chains:

- `test_campaign` depended on `test_owner`
- tests often depended on one or both without showing the relevant scenario
- understanding failures required opening `conftest.py`

The replacement is explicit factory-driven Arrange code in the test itself. The test now shows which attributes matter for the rule being exercised.

## Why `api_request` Was Kept And `api_client_factory` Was Removed

The suite now prefers `api_request` as the default API test interface.

That decision was made because:

- most backend API tests read more clearly as synchronous request/response flows
- `api_request` hides only transport plumbing, not scenario data
- the separate `api_client_factory` was no longer used and added another way to test the same thing

Keeping one primary request fixture makes the suite more consistent.

## Why Factory Fixtures Commit By Default

For API tests, factory-created rows usually need to be visible to the request handler, which runs in a separate SQLAlchemy session. If a factory only flushes without committing, the request may not be able to see the data, and SQLite can lock when two sessions try to work on the same file-backed database.

For that reason, the factory fixtures commit by default when they manage their own session.

They still allow a `db_session=` override for tests that intentionally need same-session setup control. This preserves flexibility without making the default path fragile.

## Intended Fixture Surface

The current intended fixture surface is:

### Infrastructure Fixtures

- `sqlite_engine`
- `db_session`
- `db_session_factory`
- `test_app`
- `api_request`
- `sync_api_test_runtime_shim`
- `postgres_test_container`
- `postgres_test_settings`

These fixtures handle plumbing, runtime wiring, and shared environment setup.

### Scenario Factory Fixtures

- `owner_factory`
- `campaign_factory`
- `entity_factory`
- `relationship_factory`

These fixtures create test data while keeping the meaningful attributes explicit in the test body.

## Practical Rule Going Forward

The working rule for backend tests is:

- use fixtures for plumbing
- use factories for records
- keep business-relevant values in the Arrange step of the test
- prefer one clear request path through `api_request`
- keep PostgreSQL integration coverage real, not simulated

If a future test requires opening `conftest.py` just to understand the scenario, the test is probably too implicit and should be rewritten.
