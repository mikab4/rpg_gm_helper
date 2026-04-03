# Config Contract Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move frontend-related backend CORS settings out of hardcoded code and into app-local configuration with a documented frontend-backend env contract.

**Architecture:** Keep frontend and backend config modules separate, but align variable naming and responsibilities so a shared config layer can be added later without redesigning runtime wiring. The backend remains responsible for CORS origin policy and the frontend remains responsible for the API base URL it calls.

**Tech Stack:** FastAPI, Pydantic Settings, pytest, Ruff, Vite env config

---

### Task 1: Add backend config coverage for CORS origins

**Files:**
- Modify: `backend/tests/test_main.py`

**Step 1: Write the failing test**

Add a test that asserts the backend allows the frontend dev origin through configured settings rather than a hardcoded constant.

**Step 2: Run test to verify it fails**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_main.py -q`
Expected: FAIL while the backend still uses hardcoded origin values.

**Step 3: Write minimal implementation**

Move CORS origins into backend settings and wire middleware from those settings.

**Step 4: Run test to verify it passes**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_main.py -q`
Expected: PASS.

### Task 2: Update backend env example

**Files:**
- Modify: `backend/.env.example`

**Step 1: Write minimal implementation**

Add a `BACKEND_CORS_ALLOWED_ORIGINS` example value using the local Vite origins.

**Step 2: Verify manually**

Confirm the example matches the frontend dev server origin and the README contract.

### Task 3: Document the config contract

**Files:**
- Modify: `README.md`

**Step 1: Write minimal implementation**

Add a short configuration contract section describing:
- backend-owned settings
- frontend-owned settings
- how `VITE_API_BASE_URL` and `BACKEND_CORS_ALLOWED_ORIGINS` relate

**Step 2: Verify manually**

Confirm the wording is explicit about origin versus API base URL.

### Task 4: Verify backend changes

**Files:**
- Verify only

**Step 1: Run focused backend tests**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_main.py -q`
Expected: PASS.

**Step 2: Run Ruff**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check`
Expected: PASS.
