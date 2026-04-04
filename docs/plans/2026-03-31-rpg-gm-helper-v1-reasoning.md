# Why This Plan

## Problem We Are Actually Solving

The immediate goal is not to build a complete RPG worldbuilding platform. The goal is to produce a working, demoable tool in about two weeks that:
- stores campaign data in a structured way
- ingests free text such as session notes
- extracts candidate entities from that text
- lets the user review those candidates before saving them
- supports search over saved information

At the same time, the project should remain a base for future learning in:
- semantic search
- model-assisted extraction
- model training
- broader backend and architecture skills

The plan is designed to hit the short-term milestone without blocking those longer-term directions.

## Why We Chose A Modular Monolith

Microservices were intentionally rejected for v1.

Reasoning:
- There is only one user and one product workflow.
- Splitting services early would add deployment, coordination, and debugging overhead before the data model is even stable.
- Search, extraction, entities, and notes are tightly connected. Splitting them now would mostly create boundaries that need to be undone or heavily revised later.

What we took instead:
- one backend application
- clear internal service boundaries
- explicit interfaces for extraction, search, and external sync

This gives most of the learning value of good architecture without paying the operational cost of distributed systems too early.

## Why The Backend Stays In Python

Python, FastAPI, and PostgreSQL are already familiar. That familiarity is not a weakness here; it is a way to protect delivery speed.

Reasoning:
- The backend contains the highest product risk in the first two weeks: schema design, extraction workflow, review flow, and search.
- Relearning the backend stack at the same time would increase the chance of ending with an incomplete demo.
- Python remains a strong choice for future NLP, extraction pipelines, and model experimentation.

So the plan keeps the backend in a known stack and moves the learning budget elsewhere.

## Why The Frontend Is TypeScript React

The user explicitly wanted at least one meaningful new thing to learn.

We considered:
- TypeScript frontend only
- full-stack TypeScript
- keeping the stack familiar and using the novelty budget on search or LLM infrastructure

We chose TypeScript frontend only because it is the best balance of learning and delivery.

Why this is the right tradeoff:
- It adds a new skill with clear portfolio value.
- It keeps the backend stable and fast to build.
- It creates a typed client-server boundary, which is useful backend/frontend experience.
- It avoids the cost of rewriting all backend work into a new ecosystem under time pressure.

Why we did not choose full-stack TypeScript:
- too much stack churn for a two-week milestone
- higher setup and debugging risk
- likely to reduce the amount of product functionality completed

## Why The Frontend Stays Thin And Isolated

Choosing React for v1 does not mean the product should absorb React-shaped architecture.

Reasoning:
- The backend owns the risky logic in this milestone: CRUD validation, extraction review, provenance, and search behavior.
- If workflow rules drift into hooks, client caches, or frontend-only abstractions, the product becomes harder to test and harder to change.
- The UI needs to move quickly, but it does not need framework-specific complexity to do that.

What we took instead:
- a separate frontend app in the same repository
- a plain typed API client at the frontend-backend boundary
- routing, forms, tables, and presentation in the frontend
- business rules, persistence rules, and workflow logic in FastAPI services

This preserves an important escape hatch: if React turns out to be the wrong fit for the admin-style UI, the CSS, UX flows, and API contracts should remain reusable enough that replacing the frontend is a bounded cost rather than a rewrite of product behavior.

## Why PostgreSQL Is The Only Database In V1

The project may later explore SQL, NoSQL, semantic search, and more advanced storage patterns. That does not justify starting with multiple datastores.

Reasoning:
- PostgreSQL is enough for structured entities, notes, relationships, extraction jobs, and keyword search.
- PostgreSQL full-text search is sufficient for the first milestone.
- Using a second database now would mostly be complexity for the sake of learning, not product need.

The plan still leaves room for later expansion:
- JSONB can hold flexible metadata without replacing the relational core
- raw note and document text is preserved for future embeddings or training
- search lives behind a service boundary so vector search can be added later

## Why Search Is Keyword Search First

Semantic search is a future goal, but it was intentionally deferred.

Reasoning:
- The first thing to validate is the product workflow, not the sophistication of retrieval.
- PostgreSQL full-text search is cheap, robust, and easy to debug.
- Good structured data plus good provenance and review is more valuable early than weak semantic search over noisy auto-generated records.

The design still prepares for semantic search later by:
- storing raw text
- preserving provenance
- isolating search logic behind a service

## Why Extraction Is Rules-First With An LLM Interface

The product idea depends on turning free text into structured records, so extraction is part of v1. But full LLM dependence was rejected as the center of the first milestone.

Reasoning:
- LLM-first extraction is attractive, but it introduces variability, prompt iteration overhead, API dependence, and harder testing.
- In a two-week build, predictable behavior matters more than ambitious automation quality.
- A review step is required anyway, so rules-based extraction can still demonstrate the workflow.

What we chose:
- a clean extraction interface
- a rules-based implementation as the default
- a future-compatible path for an optional LLM-backed implementation

This keeps the demo stable while preserving the future learning path.

## Why Kanka Is Deferred

Kanka may still be useful later as an inspiration source or optional integration, but it is no longer part of the current v1 milestone.

Reasoning:
- It is not central to validating the core workflow of source text, extraction, review, and canonical persistence.
- It adds schema and interface work for a feature that may never be implemented.
- The current milestone is stronger if it stays focused on the product's own source of truth.

The chosen boundary is now:
- this app is the source of truth
- Kanka is deferred from v1
- the schema should not reserve tables for Kanka until the integration is reintroduced with a concrete use case

## Why Auth Is Deferred But Not Ignored

Single-user local-first is the correct default for the first milestone.

Reasoning:
- Auth, sessions, password flows, and multi-user ownership would consume a large part of the two-week budget.
- None of those are necessary to validate the core workflow.

However, ignoring auth completely would be shortsighted. So the plan reserves for future auth by:
- including an owner placeholder in the schema
- avoiding global implicit campaign assumptions
- making campaign ownership explicit in API shapes

That keeps later auth work moderate instead of forcing a rewrite.

## Why The UI Is Admin-Style

A polished product UI was rejected for v1.

Reasoning:
- The main learning and product value in this slice are backend workflow, data modeling, extraction, and review.
- An admin-style interface is enough to demo those clearly.
- Spending too much time on visual polish would reduce the amount of actual product behavior delivered.

The frontend should still be clean and typed, but it does not need a strong design system or heavy client architecture in the first milestone.

## Why The Data Model Uses A Generic Entity Table

We considered a more specialized schema with separate tables for characters, locations, factions, and other record types.

We rejected that for v1.

Reasoning:
- The exact domain model is not stable yet.
- A generic entity table is faster to implement and easier to evolve in the early stage.
- The review and search workflows care more about consistent storage and filtering than about perfect type specialization.

The tradeoff:
- some type-specific validation is weaker in v1
- but iteration speed is much better

This is the right tradeoff for an early product slice.

## What We Intentionally Deferred

These were intentionally excluded because they add complexity without helping the first milestone enough:
- multi-user auth
- permissions
- semantic or vector search
- model training pipeline
- microservices
- Redis or background queue infrastructure
- separate NoSQL storage
- Kanka export and sync
- fully automatic write-back from extracted notes without review

Deferring these is not avoidance. It is how the plan stays coherent and achievable.

## Why This Plan Is A Good Fit

This plan is a good fit because it balances four things that usually conflict:
- a demoable product in two weeks
- one meaningful new technology to learn
- a backend and data model you still own
- a clean path toward more advanced future features

In short:
- it is ambitious enough to be worth showing
- narrow enough to actually finish
- simple enough to debug
- extensible enough to keep growing after the milestone
