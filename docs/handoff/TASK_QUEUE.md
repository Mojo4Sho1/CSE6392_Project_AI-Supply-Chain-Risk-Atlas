# Task Queue

**Last updated:** 2026-03-26
**Owner:** Joe

## Purpose

Prioritized backlog of discrete, agent-executable tasks. After completing assigned tasks, agents must:
1. Mark completed tasks `done` below.
2. Update `CURRENT_STATUS.md` with what was accomplished.
3. Update `NEXT_TASK.md` to point at the next `queued` task(s).

## Status Key

- `done` — completed and verified
- `active` — currently being worked on (should match `NEXT_TASK.md`)
- `queued` — ready to start, dependencies met
- `blocked` — cannot start, dependency not met

---

## Phase 0: Scaffolding

| ID | Status | Task | Specs to Read | Acceptance Criteria |
|----|--------|------|---------------|---------------------|
| T-001 | done | CSV cleanup: remove 4 low-value columns | `artifact-schemas.md` | CSV has 9 columns, no `ranking_signal`/`selection_method`/`eligible`/`selection_source` |
| T-002 | done | Spec reconciliation | `data-sourcing-and-eligibility.md`, `artifact-schemas.md`, `decision-log.md` | Specs match CSV schema; DEC-008 recorded |
| T-003 | done | Create campaign plan | — | `CAMPAIGN_PLAN.md` exists with all phases |
| T-004 | done | Create task queue | — | `TASK_QUEUE.md` exists (this file) |
| T-005 | done | Create quick-reference index | All specs (for extraction) | `QUICK_REFERENCE.md` exists with enums, schemas, CLI contract |
| T-006 | done | Update handoff docs | — | `CURRENT_STATUS.md` and `NEXT_TASK.md` reflect current state |

## Phase 1: M1 — Ingestion & Eligibility

| ID | Status | Task | Specs to Read | Acceptance Criteria |
|----|--------|------|---------------|---------------------|
| T-007 | done | Implement `model_id` normalization utility + tests | `artifact-schemas.md` (normalization section) | Function passes deterministic test cases; output matches spec 7-step algorithm |
| T-008 | done | Implement CSV parser with v1 schema validation + tests | `data-sourcing-and-eligibility.md`, `artifact-schemas.md` | Validates 9-column header; parses shorthand likes; rejects legacy schemas |
| T-009 | done | Implement artifact discovery with hint support + tests | `data-sourcing-and-eligibility.md`, `extraction-and-normalization.md` | Uses `dependency_artifact_url` hint when present; discovers artifacts otherwise; handles unreachable repos |
| T-010 | done | Implement eligibility evaluation + tests | `data-sourcing-and-eligibility.md`, `artifact-schemas.md` | All canonical `eligibility_reason_code` values mapped; at least one eligible + one ineligible test case |
| T-011 | done | Assemble `ingest_repo_artifacts.py` with CLI contract | `pipeline-execution-contract.md` | `--help` works; CLI flags match contract; exit codes correct |
| T-012 | done | Create Makefile with `ingest`/`test` targets | `AGENTS.md` (automation section) | `make test` runs pytest; `make ingest` runs ingestion script |
| T-013 | done | End-to-end M1 smoke test | `testing-and-validation.md` | Script processes all 13 CSV rows; manifests validate against schema |

## Phase 2: M2 — OSV Scan & Normalization

| ID | Status | Task | Specs to Read | Acceptance Criteria |
|----|--------|------|---------------|---------------------|
| T-014 | done | Install/verify OSV-Scanner | `extraction-and-normalization.md` | `osv-scanner --version` works in conda env |
| T-015 | done | Implement `run_osv_scan.py` + tests | `extraction-and-normalization.md`, `artifact-schemas.md`, `pipeline-execution-contract.md` | Raw + normalized JSON for all eligible models; schema-valid |
| T-016 | done | Add `make scan` target | — | `make scan` runs OSV scan script |

## Phase 3: M3 — Graph Construction

| ID | Status | Task | Specs to Read | Acceptance Criteria |
|----|--------|------|---------------|---------------------|
| T-017 | done | Implement `build_risk_graph.py` + tests | `graph-semantics-and-metrics.md`, `artifact-schemas.md`, `pipeline-execution-contract.md` | `global.graphml` loads; correct node/edge types; package deduplication verified |
| T-018 | done | Add `make graph` target | — | `make graph` runs graph build script |

## Phase 4: M4 — Reporting & Atlas

| ID | Status | Task | Specs to Read | Acceptance Criteria |
|----|--------|------|---------------|---------------------|
| T-019 | done | Implement `generate_atlas_reports.py` + tests | `graph-semantics-and-metrics.md`, `artifact-schemas.md`, `pipeline-execution-contract.md` | `summary.json` + `summary.csv` + `figures/` produced; schema-valid |
| T-020 | done | Add `make report` and `make all` targets | — | `make all` runs full pipeline end-to-end |

## Phase 5: Polish, Submission & Showcase

| ID | Status | Task | Specs to Read | Acceptance Criteria |
|----|--------|------|---------------|---------------------|
| T-021 | done | Full pipeline validation (`make all`) | `PROJECT_CHECKLIST.md` | All milestone gates pass; cross-phase verification suite passes |
| T-022 | done | Final documentation pass | All handoff + spec docs | All docs current; no stale references; README accurate |
| T-023 | done | Draft dashboard showcase spec and route docs | `dashboard-showcase.md`, `_INDEX.md` | Dashboard spec exists; routing docs point future agents to it consistently |
| T-024 | done | Implement local Dash/Plotly dashboard + tests | `dashboard-showcase.md`, `graph-semantics-and-metrics.md`, `artifact-schemas.md` | Local dashboard loads graph/report artifacts, supports required search/filters/details, and test coverage exists |
| T-025 | done | Add `make dashboard` target and demo instructions | `dashboard-showcase.md`, `AGENTS.md` | `make dashboard` launches the local app with documented defaults |
| T-026 | done | Review live dashboard UX and lock redesign direction | `docs/dashboard_redesign_plan.md`, `CURRENT_STATUS.md` | The repo contains a staged redesign plan that locks the graph-first shell direction, retains Plotly through Stages 0-2, and defers Cytoscape migration to Stage 3 |
| T-028 | done | Create simple LaTeX final report scaffold | `README.md`, `CURRENT_STATUS.md` | `paper/final_report.tex` exists with project-specific starter content and `paper/README.md` explains local/Overleaf usage |
| T-029 | done | Dashboard redesign Stage 0: audit and refactor preparation | `docs/dashboard_redesign_plan.md`, `dashboard-showcase.md`, `CURRENT_STATUS.md` | Theme/token organization exists, branding asset placement is unambiguous, current dashboard behavior still works, and Stage 1 can start without rediscovering dashboard structure |
| T-030 | active | Dashboard redesign Stage 1: new app shell, layout, and theme | `docs/dashboard_redesign_plan.md`, `dashboard-showcase.md`, `AGENTS.md` | Dashboard uses a graph-first app shell with top bar / left sidebar / center graph / right inspector, while preserving current analytical semantics and still using Plotly |
| T-031 | blocked | Dashboard redesign Stage 2: branding pass and visual refinement | `docs/dashboard_redesign_plan.md`, `CURRENT_STATUS.md` | Branding, panel styling, badges, legend, and empty states feel cohesive without changing analytical behavior |
| T-032 | blocked | Dashboard redesign Stage 3: Cytoscape migration | `docs/dashboard_redesign_plan.md`, `dashboard-showcase.md`, `AGENTS.md` | Cytoscape replaces Plotly cleanly while preserving graph semantics, label strategy, and the existing data/view-model layer |
| T-033 | blocked | Dashboard redesign Stage 4: selection workflow and inspector redesign | `docs/dashboard_redesign_plan.md`, `CURRENT_STATUS.md` | Selecting a node drives clear graph focus, neighborhood highlighting, and a structured right-side inspector |
| T-034 | blocked | Dashboard redesign Stage 5: filters, search, and linked summary views | `docs/dashboard_redesign_plan.md`, `dashboard-showcase.md` | Search, filters, visible counts, and clickable summary views stay synchronized and feel investigation-friendly |
| T-035 | blocked | Dashboard redesign Stage 6: final polish for local research use | `docs/dashboard_redesign_plan.md`, `CURRENT_STATUS.md` | Loading states, spacing, focus/hover behavior, and overall presentation feel complete and comfortable for repeated local exploration |
