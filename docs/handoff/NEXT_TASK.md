# Next Task

**Last updated:** 2026-03-24
**Owner:** Joe

## Task summary

Implement the optional local dashboard showcase described in `docs/specs/dashboard-showcase.md`, then add the launch target and demo instructions so the repo has a polished local presentation layer over the completed M1-M4 artifacts.

**Task queue references:** T-024 through T-025 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Phase 5 validation/documentation is complete: the M1-M4 pipeline is validated, `README.md`/handoff/spec docs are aligned, and `make validate` now bundles the local verification workflow.
- `docs/specs/dashboard-showcase.md` already defines the showcase contract, so the next batch can move straight into implementation.
- The dashboard is explicitly optional for the core pipeline, which makes it a clean final batch without reopening the validated M1-M4 contracts.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-024:** Implement `scripts/run_dashboard.py` and any supporting loader/transform helpers needed to read `graphs/global.graphml`, `reports/summary.json`, and `reports/summary.csv`
2. **T-024:** Add automated tests for artifact loading, dashboard-ready transformations, and core search/filter/detail behavior
3. **T-025:** Add `make dashboard`, document the launch flow, and re-run the validation/test suite

## Scope (in)

- Implement the local read-only Dash/Plotly showcase contract from `docs/specs/dashboard-showcase.md`
- Load the graph/report artifacts once at startup and transform them into dashboard-ready in-memory structures
- Deliver the required overview, graph explorer, model detail, and package detail surfaces
- Support the required searches, filters, and selection-driven detail panel behavior
- Add unit and smoke tests for new dashboard code (per `AGENTS.md` testing policy)
- Add `make dashboard` and README demo instructions for the local launch workflow

## Scope (out)

- Changes to the validated M1-M4 pipeline outputs or schemas unless the dashboard work uncovers a genuine contract bug
- Hosted deployment, authentication, write-back workflows, or triggering pipeline stages from the dashboard
- New graph edge types or composite risk-scoring work

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `graphs/global.graphml`
  - `reports/summary.json`
  - `reports/summary.csv`
  - `figures/reused_vulnerable_packages.png`
  - `figures/impacted_model_count_distribution.png`
- Specs (read only what's needed):
  - `docs/specs/dashboard-showcase.md` — dashboard runtime contract, required views, interactions, and tests
  - `docs/specs/graph-semantics-and-metrics.md` — graph typing and node/edge attribute expectations
  - `docs/specs/artifact-schemas.md` — report schema and enum contracts
  - `docs/specs/testing-and-validation.md` — required test layers and validation expectations for new code

## Implementation notes

- Keep the dashboard strictly read-only over the existing artifacts; it must not ingest, scan, rebuild the graph, or regenerate reports
- Treat `graphs/global.graphml` as the source of truth for topology and `reports/summary.json` / `reports/summary.csv` as the source of truth for precomputed metrics
- Parse `vuln_ids_json` from GraphML package nodes as described in `docs/specs/dashboard-showcase.md`
- Run `pytest` / `make test` after every code change
- Treat expected failure paths as normal outcomes, not crashes

## Acceptance criteria (definition of done)

- The dashboard loads the existing graph/report artifacts locally and exposes the required overview, explorer, and detail surfaces
- Search, filter, and selection behavior works as specified in `docs/specs/dashboard-showcase.md`
- `make dashboard` launches the app with the documented defaults
- All tests pass (`make test`)
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `python scripts/run_dashboard.py --help` works
- [ ] `make test` passes
- [ ] `make dashboard` launches with the documented defaults
- [ ] Dashboard startup reads `graphs/global.graphml`, `reports/summary.json`, and `reports/summary.csv` successfully
- [ ] Required search/filter/detail interactions are covered by automated tests
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-024 through T-025 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 5
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed milestone checklist state or showcase-track readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on the next queued batch after dashboard implementation, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- Keep the dashboard separate from the validated pipeline stages; avoid adding any code path that mutates existing artifacts
- Graph rendering can get visually noisy with the full atlas; keep filtering/search central so the local demo remains usable
- Do not let dashboard convenience code introduce new schema assumptions that contradict `graphs/global.graphml` or `reports/summary.json`
