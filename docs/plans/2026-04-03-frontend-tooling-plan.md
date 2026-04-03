# Frontend Tooling Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add strict TypeScript-aware linting, deterministic formatting, and a local pre-commit hook for the frontend.

**Architecture:** Keep the toolchain small and explicit. Use ESLint for correctness, typed linting, and React hook safety; use Prettier for formatting only; wire a simple repo-local git hook instead of adding hook-management dependencies.

**Tech Stack:** ESLint, typescript-eslint, eslint-plugin-react-hooks, Prettier, Vite, TypeScript, bash git hook

---

### Task 1: Add frontend tooling dependencies and scripts

**Files:**
- Modify: `frontend/package.json`

**Steps:**
1. Add ESLint, typescript-eslint, React hooks linting, Prettier, and supporting packages as frontend dev dependencies.
2. Add `lint`, `lint:fix`, `format`, and `format:check` scripts.

### Task 2: Add lint and format configuration

**Files:**
- Create: `frontend/eslint.config.js`
- Create: `frontend/.prettierrc.json`
- Create: `frontend/.prettierignore`
- Create: `frontend/tsconfig.eslint.json`

**Steps:**
1. Configure ESLint flat config with base JS rules, typed TypeScript rules, React hooks rules, and Prettier compatibility.
2. Configure Prettier with stable formatting defaults.
3. Add a dedicated TypeScript config for typed linting.

### Task 3: Add local hook wiring

**Files:**
- Create: `.githooks/pre-commit`

**Steps:**
1. Add a pre-commit hook that targets staged frontend files only.
2. Run Prettier on staged frontend text files and ESLint `--fix` on staged TypeScript files.
3. Re-stage modified files so the commit contains the enforced output.

### Task 4: Add a local learning note

**Files:**
- Create locally and exclude from git: `learning/frontend-tooling-notes.md`

**Steps:**
1. Write a short note explaining each tool and why this repo uses it.
2. Exclude the `learning/` folder from git locally instead of expanding tracked ignore rules.

### Task 5: Verify the setup

**Files:**
- Verify: `frontend/package.json`
- Verify: `frontend/eslint.config.js`
- Verify: `.githooks/pre-commit`

**Steps:**
1. Install frontend dependencies.
2. Set `core.hooksPath` to `.githooks`.
3. Run `npm run lint`, `npm run format:check`, and `npm run build` in `frontend/`.
4. Fix any config issues before closing the task.
