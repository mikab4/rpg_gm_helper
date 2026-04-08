# Possible Technical Debt

## App-managed database wiring

Current recommendation for the reviewed import-time DB issue was to remove module-level globals and keep explicit factories in `backend/app/db.py`.

A stronger long-term alternative is to create the SQLAlchemy engine during app bootstrap, store it on FastAPI app state, and expose sessions through a FastAPI dependency.

Why this may be worth doing later:
- It fits the app-factory direction better than process-global engine state.
- It makes per-app-instance DB wiring more explicit for tests and future runtime setup.
- It gives a cleaner place to manage engine lifecycle and disposal once DB-backed routes are added.

Why it was deferred now:
- Nothing in the scaffold currently consumes the database layer.
- Adding app-state and dependency wiring now would be extra abstraction before there is a real DB call path to justify it.
- The explicit factory approach already removes the current brittleness without introducing more lifecycle machinery.

## Frontend API schema validation

Current recommendation for the reviewed frontend API client issue was to keep a thin shared fetch helper that returns `unknown` and require endpoint-specific parsing, starting with the health endpoint.

A stronger long-term alternative is to introduce a schema validation library such as Zod at the network boundary and define explicit response schemas for API contracts.

Why this may be worth doing later:
- It would provide runtime validation and inferred TypeScript types from the same source.
- It would scale better once the frontend starts consuming multiple CRUD and search endpoints.
- It would make backend/frontend drift fail in a more standardized and inspectable way.

Why it was deferred now:
- The scaffold currently has only one real response contract.
- A schema library would add dependency and abstraction overhead before there is enough API surface to justify it.
- Endpoint-local parsing already removes the misleading unchecked cast without committing the project to a validation framework yet.

## Repeated frontend request-state pages

Current recommendation for the reviewed frontend CRUD pages was to leave the repeated `loading/error/ready` route pattern in place in pages such as [CampaignFormPage](/home/mikab4/projects/rpg_gm_helper/.worktrees/crud_entities_campaign_frontend/frontend/src/routes/CampaignFormPage.tsx) and [EntityFormPage](/home/mikab4/projects/rpg_gm_helper/.worktrees/crud_entities_campaign_frontend/frontend/src/routes/EntityFormPage.tsx).

A stronger long-term alternative is to introduce a small route-level helper or wrapper for request-state pages once more CRUD surfaces repeat the same shape.

Why this may be worth doing later:
- It would reduce repeated conditional rendering across CRUD routes.
- It would make route components easier to scan by pushing common request-state composition into one place.
- It would lower maintenance cost once more forms and detail pages follow the same fetch-state structure.

Why it was deferred now:
- The repetition is still small and obvious in v1.
- Extracting a shared abstraction too early risks hiding simple route behavior behind indirection.
- There are not enough route variants yet to prove the right reusable shape.

## Forms seeded from initial props

Current recommendation for the reviewed form components was to keep [CampaignForm](/home/mikab4/projects/rpg_gm_helper/.worktrees/crud_entities_campaign_frontend/frontend/src/components/CampaignForm.tsx) and [EntityForm](/home/mikab4/projects/rpg_gm_helper/.worktrees/crud_entities_campaign_frontend/frontend/src/components/EntityForm.tsx) state initialized from `initialValues`, because these forms currently mount fresh per route.

A stronger long-term alternative is to either remount forms explicitly with a stable `key` or add controlled resync behavior if future usage expects prop changes to refresh the form in place.

Why this may be worth doing later:
- It prevents stale form state bugs if a parent starts swapping records without remounting.
- It makes the form behavior more explicit for future reuse outside route-local mount cycles.
- It avoids hidden coupling between routing behavior and form correctness.

Why it was deferred now:
- Current usage mounts these forms fresh per route transition.
- Adding sync effects now would increase complexity and create extra state-reset edge cases without solving a live bug.
- The simpler mount-fresh assumption is still correct for the current CRUD flow.

## Campaign delete post-success flow

Current recommendation for the reviewed campaign delete flow was to keep the explicit post-delete confirmation state in [CampaignWorkspacePage](/home/mikab4/projects/rpg_gm_helper/.worktrees/crud_entities_campaign_frontend/frontend/src/routes/CampaignWorkspacePage.tsx) rather than immediately redirecting to `/campaigns`.

A stronger long-term alternative is to standardize destructive CRUD success flows around automatic navigation back to the parent list once the surrounding router/test setup makes that path boring and reliable.

Why this may be worth doing later:
- It is closer to the usual CRUD admin expectation after deleting a record.
- It would make campaign delete behave more like other parent-list flows in the app.
- It may reduce one extra confirmation surface if users prefer being returned directly to the registry.

Why it was deferred now:
- The current confirmation screen is a valid product choice and is not a correctness bug.
- Immediate redirect introduced router/test-environment issues in the current setup, so forcing it now would add complexity for limited product gain.
- The confirmation state is explicit and reliable while the app is still stabilizing its CRUD flows.
