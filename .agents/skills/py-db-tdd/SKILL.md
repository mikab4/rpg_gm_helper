---
name: py-db-tdd
description: Use when writing, refactoring, or reviewing Python backend tests in this repository, especially pytest fixture design, SQLAlchemy setup, API tests, and database-backed scenarios.
---

# Py DB TDD

Write backend tests as executable rules. A reader should be able to see the scenario, the database state that matters, and the business rule being checked without opening `conftest.py`.

This skill is self-contained for this repository. It combines readable test-writing rules with repo-specific guidance for pytest fixtures, SQLAlchemy setup, and API tests under `backend/tests/`.

## When To Use

- Writing or refactoring tests in `backend/tests/`
- Reviewing pytest fixtures or factory design
- Converting named scenario fixtures into explicit test setup
- Deciding whether setup belongs in a fixture, a factory, or directly in the test
- Working on FastAPI API tests that need database state

## Core Rules

### 1. Keep AAA Visible

Every test should show a clear Arrange, Act, Assert flow.

- Arrange: create the rows, inputs, and collaborators that matter
- Act: make the API call or invoke the service
- Assert: verify the single rule under test

Use blank lines or brief `# Arrange`, `# Act`, `# Assert` comments when needed.

### 2. Name Tests Like Requirements

Prefer names that read like a rule:

`test_<behavior>_<scenario>_<expected_result>`

If the name is long, keep it long. Clarity is cheaper than guesswork.

### 3. Prefer DAMP Over DRY

Tests in this repo should be boring and explicit.

- Keep setup close to the test
- Duplicate a few lines if that keeps the scenario visible
- Do not hide the story behind helper stacks or deep fixture chains

### 4. Avoid Logic In Tests

A test body should be a straight line.

- Do not loop over scenarios inside the test
- Do not branch with `if`
- Do not compute expected values with test-side logic
- Use `pytest.mark.parametrize` when multiple visible cases help

### 5. One Test, One Rule

A test should fail for one reason.

- Keep assertions focused on the behavior named by the test
- Split tests when a failure would be ambiguous

## Fixture Rules For This Repo

### 6. Use Factory Fixtures For Scenario Data

Prefer fixtures that return factories, not fixed rows with hidden meaning.

Good:

```python
def test_create_campaign_returns_created_record(api_request, owner_factory) -> None:
    owner = owner_factory(
        email="gm@example.com",
        display_name="Local GM",
    )

    response = api_request(
        "POST",
        "/api/campaigns",
        json={"owner_id": str(owner.id), "name": "Iron Vale"},
    )

    assert response.status_code == 201
```

Bad:

```python
def test_create_campaign_returns_created_record(api_request, test_owner) -> None:
    response = api_request(
        "POST",
        "/api/campaigns",
        json={"owner_id": str(test_owner.id), "name": "Iron Vale"},
    )
```

In the bad version, the scenario depends on hidden knowledge from `conftest.py`.

### 7. Fixtures Handle Plumbing, Tests Handle Scenario

Use fixtures for infrastructure:

- sqlite engine setup
- Postgres container lifecycle
- settings loading
- API client wiring
- session factories

Use the test body for scenario meaning:

- which owner exists
- which campaign belongs to whom
- which entity type is present
- which relationship is overdue, legacy, cross-campaign, or invalid

The scenario belongs in the test because that is what the test is documenting.

### 8. Layer Fixture Scopes By Cost

Use wide scopes for expensive infrastructure and function scope for data isolation.

- `session` or `module` scope: container startup, test settings, schema bootstrap
- function scope: per-test rows, per-test sessions, scenario-specific data

For this repo, fixtures like `postgres_test_container` and `postgres_test_settings` are infrastructure fixtures. They should not carry scenario meaning.

### 9. Avoid Named Scenario Fixtures

Do not build fixture catalogs like:

- `campaign_with_two_entities`
- `owner_with_duplicate_campaign`
- `relationship_with_missing_target`

That style hides the rule in another file and forces the reader to hunt for meaning.

Prefer combining generic factories in the test:

```python
def test_list_campaigns_supports_owner_filter(
    api_request,
    owner_factory,
    campaign_factory,
) -> None:
    owner = owner_factory(email="gm@example.com", display_name="Local GM")
    second_owner = owner_factory(email="other@example.com", display_name="Other GM")
    campaign_factory(owner=owner, name="Iron Vale")
    campaign_factory(owner=second_owner, name="Starfall")

    response = api_request("GET", "/api/campaigns", params={"owner_id": str(owner.id)})

    assert [listed_campaign["name"] for listed_campaign in response.json()] == ["Iron Vale"]
```

Three setup lines are usually better than one mysterious fixture.

### 10. Prefer Explicit Dependencies Over `autouse`

The test signature should tell the story of what the test needs.

- If a test needs API access, include `api_request`
- If a test needs DB setup, include `db_session_factory` or a factory fixture
- If a test needs monkeypatching, include `monkeypatch`

Avoid `autouse=True` except for truly universal plumbing that would otherwise make the suite unstable or unaffordable.

### 11. Use `db_session_factory` Only When Shared Session State Matters

Factories are the default. Reach for `db_session_factory()` when the scenario needs a shared transaction or linked rows created in one session.

Good uses:

- create multiple related rows before one query
- persist and refresh a record before reading its generated ID
- build cross-row state that is clearer in one explicit session block

If a single `campaign_factory()` or `entity_factory()` call already tells the story, use that instead.

### 12. Do Not Over-Factory Simple Cases

Factories are a tool, not a religion.

If one direct model instantiation inside a `db_session_factory()` block is clearer than another layer of abstraction, prefer the clearer option.

Example:

```python
with db_session_factory() as db_session:
    stored_entity = Entity(
        campaign_id=stored_campaign.id,
        type="person",
        name="Magistrate Ilya",
        summary="Before update",
    )
    db_session.add(stored_entity)
    db_session.commit()
    db_session.refresh(stored_entity)
```

That is acceptable because the scenario remains obvious.

## Review Checklist

- Can the reader understand the starting data without opening `conftest.py`?
- Does the test body show Arrange, Act, Assert clearly?
- Are fixtures doing plumbing rather than hiding business meaning?
- Would a factory fixture make the scenario more explicit than a named fixture?
- Is `db_session_factory()` used because shared session setup matters, not by habit?
- Is `autouse` avoided unless it is truly universal infrastructure?
- Does the test fail for one clear reason?

## Repo Examples To Follow

- `backend/tests/conftest.py`
- `backend/tests/factories.py`
- `backend/tests/test_campaigns_api.py`
- `backend/tests/test_entities_api.py`

## Giacomelli Rule For This Repo

Fixtures handle plumbing. Scenario data stays in the test.
