# Task Queue

**Last updated:** 2026-03-24
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
| T-019 | active | Implement `generate_atlas_reports.py` + tests | `graph-semantics-and-metrics.md`, `artifact-schemas.md`, `pipeline-execution-contract.md` | `summary.json` + `summary.csv` + `figures/` produced; schema-valid |
| T-020 | queued | Add `make report` and `make all` targets | — | `make all` runs full pipeline end-to-end |

## Phase 5: Polish, Submission & Showcase

| ID | Status | Task | Specs to Read | Acceptance Criteria |
|----|--------|------|---------------|---------------------|
| T-021 | queued | Full pipeline validation (`make all`) | `PROJECT_CHECKLIST.md` | All milestone gates pass; cross-phase verification suite passes |
| T-022 | queued | Final documentation pass | All handoff + spec docs | All docs current; no stale references; README accurate |
| T-023 | queued | Draft dashboard showcase spec and route docs | `dashboard-showcase.md`, `_INDEX.md` | Dashboard spec exists; routing docs point future agents to it consistently |
| T-024 | queued | Implement local Dash/Plotly dashboard + tests | `dashboard-showcase.md`, `graph-semantics-and-metrics.md`, `artifact-schemas.md` | Local dashboard loads graph/report artifacts, supports required search/filters/details, and test coverage exists |
| T-025 | queued | Add `make dashboard` target and demo instructions | `dashboard-showcase.md`, `AGENTS.md` | `make dashboard` launches the local app with documented defaults |
