# CRUD Operations Test Issues

## Purpose

This document records the full sequence of problems, reviewer feedback, rejected fixes, and the final solution used for the CRUD API tests in the `CRUD_campaign_entity` worktree.

The important constraint that shaped the final outcome was:

- production CRUD code should remain sync end to end
- test problems should be solved in the test harness, not by warping the app into a fake async design

## Original Problem

The first version of the CRUD tests in:

- `backend/tests/test_campaigns_api.py`
- `backend/tests/test_entities_api.py`

were not real API tests.

They called route functions directly, which meant they skipped:

- FastAPI request parsing
- dependency injection
- query/path/body binding
- OpenAPI-facing validation behavior
- automatic `422` responses

That matched the reviewer criticism: the tests exercised route and service logic, but not the HTTP boundary.

## First Attempt: Real HTTP Tests Through Uvicorn

The first correction replaced direct function calls with real HTTP requests by:

1. creating a test app
2. overriding `get_db_session`
3. starting Uvicorn in a background thread
4. sending requests to a bound local TCP port

This did turn the CRUD tests into real API tests.

It also immediately introduced a new failure:

- the sandbox rejected socket binding with `PermissionError: [Errno 1] Operation not permitted`

So this approach was functionally correct, but operationally wrong for this environment.

## Reviewer Pushback

The reviewer then pushed back on the live-socket solution and said app-level tests should be in-process with:

- `httpx.ASGITransport`
- or `TestClient`

That target was correct, but there was a deeper blocker: in-process sync FastAPI execution was hanging.

## Root Cause Investigation

At this point the work switched from changing harnesses blindly to reproducing the failure below the CRUD code.

### Minimal Reproductions

The following facts were established:

1. an `async def` FastAPI route completed under `httpx.ASGITransport`
2. a trivial `def` FastAPI route hung under `httpx.ASGITransport`
3. `asyncio.to_thread()` worked
4. `anyio.to_thread.run_sync()` hung

That narrowed the failure boundary from:

- "CRUD tests are broken"

to:

- "the in-process sync execution path is broken in this environment"

The proven statement at that stage was narrow:

- the issue reproduced below the CRUD code
- it involved the in-process sync path
- `anyio.to_thread.run_sync()` was implicated directly

## Rejected Intermediate Fixes

Several narrower fixes were tried before the final solution.

### Attempt 1: Async CRUD Boundary

One temporary solution was:

1. make the CRUD routes `async def`
2. make the DB dependency async
3. keep the service and SQLAlchemy layers sync
4. use in-process `httpx.ASGITransport`

This worked and the tests passed.

It was then explicitly rejected after discussion because:

- sync DB work was being called directly from async routes
- that risks blocking the event loop
- it was the wrong steady-state design
- it made production code worse just to satisfy tests

This branch no longer uses that approach.

### Attempt 2: Patch AnyIO Worker Execution In Tests

The next idea was to keep production code sync and patch the broken worker path in tests.

Two variants were tried:

- replacing AnyIO worker execution with the default `asyncio` executor
- replacing it with a dedicated `ThreadPoolExecutor`

Results:

- the default executor patch did not solve the hangs
- the dedicated executor improved one minimal reproduction
- it still failed on real FastAPI paths with response models and dependency cleanup

So patching only the AnyIO worker backend was not enough.

### Attempt 3: Keep Async pytest API Tests

Even after the app was returned to sync routes and the threadpool patches improved, the CRUD API tests still hung when written as:

- `pytest.mark.anyio`
- async test functions
- async client fixture usage

That led to a second refinement:

- keep real HTTP requests
- keep `httpx.ASGITransport`
- but stop depending on the async pytest runner for the CRUD files

## Final Solution

The final accepted solution keeps the production CRUD code sync and fixes the tests only at the harness layer.

### Production Code

The CRUD boundary is sync again:

- `backend/app/api/dependencies.py`
- `backend/app/api/routes/campaigns.py`
- `backend/app/api/routes/entities.py`

That means:

- sync routes
- sync DB dependency
- sync services
- sync SQLAlchemy session usage

### Test Harness

The final CRUD test harness uses:

- in-process `httpx.ASGITransport`
- a real FastAPI app fixture
- a real `get_db_session` override
- test-only monkeypatches to bypass the broken threadpool path

The key patch lives in:

- `backend/tests/conftest.py`

It replaces:

- `starlette.concurrency.run_in_threadpool`
- `fastapi.routing.run_in_threadpool`
- `fastapi.dependencies.utils.run_in_threadpool`
- `fastapi.concurrency.run_in_threadpool`
- `anyio.to_thread.run_sync`

with inline test-only call paths.

Why both layers are patched:

- FastAPI and Starlette use `run_in_threadpool()` for sync routes, dependency solving, and response serialization
- FastAPI also uses `anyio.to_thread.run_sync()` directly inside `contextmanager_in_threadpool()` for sync generator dependency enter/exit
- patching only one of those layers still left real CRUD requests hanging

This keeps the HTTP stack real while avoiding the broken worker-thread machinery in this environment.

The shim is intentionally scoped only to the CRUD HTTP test fixtures:

- `api_request`
- `api_client_factory`

It is not applied globally across the whole backend test suite.

### CRUD Test Style

The CRUD API tests were also changed from async pytest tests to plain sync pytest tests that still issue real HTTP requests.

They now use a helper fixture in `backend/tests/conftest.py`:

- `api_request`

That helper internally:

1. creates an `httpx.ASGITransport`
2. creates an `httpx.AsyncClient`
3. sends a real request
4. returns the response through `asyncio.run(...)`

This avoids relying on the flaky async pytest runner path for the CRUD files while preserving real request behavior.

## What The Final Tests Still Cover

The final CRUD tests are still real API tests.

They exercise:

- HTTP request and response flow
- path and query parameter binding
- body parsing
- FastAPI dependency injection
- request validation and `422` responses
- response models
- service-backed CRUD behavior

What they do not try to verify anymore is FastAPI’s actual production threadpool behavior in this environment. That is the deliberate test-only compromise.

## Final File Changes

Production boundary reverted to sync:

- `backend/app/api/dependencies.py`
- `backend/app/api/routes/campaigns.py`
- `backend/app/api/routes/entities.py`

Test harness and test files:

- `backend/tests/conftest.py`
- `backend/tests/test_campaigns_api.py`
- `backend/tests/test_entities_api.py`

The earlier minimal “ASGITransport supports sync routes” regression test was removed because it was misleading once the shim became part of the test harness. Under the shim, that test only proved that the patched test environment could execute a sync route in-process, not that the underlying unpatched runtime stack was healthy.

## Final Verification

Fresh verification after the final sync-production solution:

- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format app tests`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check app tests`
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_main.py tests/test_campaigns_api.py tests/test_entities_api.py tests/test_request_schemas.py`

Result:

- `ruff` clean
- `30 passed`

## Summary

The debugging path went through these stages:

1. direct route-function tests were identified as insufficient
2. a live Uvicorn server made them real API tests but failed in the sandbox
3. in-process sync execution was isolated as the real broken boundary
4. an async-route workaround was tried and then rejected as the wrong production design
5. partial AnyIO worker patches were tried and found incomplete
6. the final fix kept production sync and moved the workaround entirely into the CRUD API test harness

That final state matches the design decision made after discussion:

- do not keep production code architecturally wrong for the sake of tests
- keep the CRUD backend sync
- accept a targeted test-only workaround for the broken in-process sync runtime path
