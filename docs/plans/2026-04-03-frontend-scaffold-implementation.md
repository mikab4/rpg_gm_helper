# Frontend Scaffold Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Finish the frontend scaffold with real routing, a shared shell, and a basic live backend health check.

**Architecture:** Keep the frontend aligned with the existing FastAPI backend surface. Add a real client-side router and a minimal typed API boundary that only covers the currently implemented backend health endpoint. Use placeholder routed pages for planned product areas rather than guessing unstable CRUD contracts.

**Tech Stack:** React 19, TypeScript, Vite, react-router-dom, Vitest, Testing Library

---

### Task 1: Add frontend test tooling

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/tsconfig.app.json`
- Create: `frontend/src/test/setup.ts`

**Step 1: Write the failing test**

Create `frontend/src/routes/__tests__/overview-page.test.tsx` with a test that renders the overview route, mocks the health API response, and expects the connected state to appear.

**Step 2: Run test to verify it fails**

Run: `npm run test -- overview-page`
Expected: FAIL because test tooling or route components do not exist yet.

**Step 3: Write minimal implementation support**

Add `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, and `jsdom`. Configure Vite test setup and TypeScript support for the test environment.

**Step 4: Run test to verify it still fails for the intended reason**

Run: `npm run test -- overview-page`
Expected: FAIL because the overview route and health client behavior are not implemented yet.

### Task 2: Create typed API boundary and stable types

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/health.ts`
- Create: `frontend/src/types/health.ts`
- Create: `frontend/src/config.ts`

**Step 1: Write the failing test**

Extend `frontend/src/routes/__tests__/overview-page.test.tsx` to assert the returned backend status is rendered after a successful request.

**Step 2: Run test to verify it fails**

Run: `npm run test -- overview-page`
Expected: FAIL because no typed health client exists.

**Step 3: Write minimal implementation**

Implement the shared API base URL config, fetch helper, health client, and health response type.

**Step 4: Run test to verify it passes**

Run: `npm run test -- overview-page`
Expected: PASS for the health status assertions.

### Task 3: Add real routing and shared shell

**Files:**
- Modify: `frontend/src/main.tsx`
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/app/AppShell.tsx`
- Create: `frontend/src/app/routes.tsx`
- Create: `frontend/src/routes/OverviewPage.tsx`
- Create: `frontend/src/routes/PlaceholderPage.tsx`

**Step 1: Write the failing test**

Add assertions that the overview route renders inside a shared shell and that navigation links for the planned app areas are visible.

**Step 2: Run test to verify it fails**

Run: `npm run test -- overview-page`
Expected: FAIL because the router and shell do not exist yet.

**Step 3: Write minimal implementation**

Install and wire `react-router-dom`. Add the shared shell, route table, overview page, and placeholder routed pages.

**Step 4: Run test to verify it passes**

Run: `npm run test -- overview-page`
Expected: PASS.

### Task 4: Refresh scaffold styling

**Files:**
- Modify: `frontend/src/styles.css`

**Step 1: Write the failing test**

No new test. Keep visual changes within the existing routed structure.

**Step 2: Write minimal implementation**

Update styles to support the shell, navigation, status card, and placeholder page layout while preserving a restrained admin-style interface.

**Step 3: Run verification**

Run: `npm run build`
Expected: PASS.

### Task 5: Verify the scaffold

**Files:**
- Verify only

**Step 1: Run focused tests**

Run: `npm run test -- --run`
Expected: PASS.

**Step 2: Run lint**

Run: `npm run lint`
Expected: PASS.

**Step 3: Run build**

Run: `npm run build`
Expected: PASS.
