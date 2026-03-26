# Campaign Plan

**Last updated:** 2026-03-26
**Owner:** Joe

## Purpose

Phased implementation roadmap for the AI Supply Chain Risk Atlas pipeline. Agents read this for long-horizon context; `NEXT_TASK.md` remains the source of truth for immediate work.

## Phase 0: Scaffolding (no code)

**Goal:** Reconcile CSV/spec drift, create agent scaffolding docs, prepare for M1.

- [x] CSV cleanup: remove low-value columns, align with spec
- [x] Spec reconciliation: update `data-sourcing-and-eligibility.md`, `artifact-schemas.md`, `decision-log.md`
- [x] Create `CAMPAIGN_PLAN.md` (this file)
- [x] Create `TASK_QUEUE.md`
- [x] Create `QUICK_REFERENCE.md`
- [x] Update `CURRENT_STATUS.md` and `NEXT_TASK.md`

**Gate:** All handoff docs current, specs match CSV, task queue seeded.

## Phase 1: M1 — Ingestion & Eligibility

**Goal:** Produce deterministic `manifest_index.json` for every CSV candidate.

- [x] Implement `model_id` normalization utility + tests (T-007)
- [x] Implement CSV parser with v1 schema validation + tests (T-008)
- [x] Implement artifact discovery with hint support + tests (T-009)
- [x] Implement eligibility evaluation with canonical reason codes + tests (T-010)
- [x] Assemble `scripts/ingest_repo_artifacts.py` with CLI contract (T-011)
- [x] Create `Makefile` with `make ingest` and `make test` targets (T-012)
- [x] End-to-end M1 smoke test (T-013)

**Gate:** `manifests/<model_id>/manifest_index.json` produced for all 13 CSV rows. At least one eligible + one ineligible path. All tests pass.

**Key specs:** `artifact-schemas.md`, `pipeline-execution-contract.md`, `data-sourcing-and-eligibility.md`, `extraction-and-normalization.md`, `testing-and-validation.md`

## Phase 2: M2 — OSV Scan & Normalization

**Goal:** Generate raw + normalized vulnerability data for eligible models.

- [x] Install/verify OSV-Scanner availability (T-014)
- [x] Implement `scripts/run_osv_scan.py` + tests (T-015)
- [x] Add `make scan` target (T-016)

**Gate:** Every eligible model has `raw.json` + `normalized.json`. All normalized files validate against schema. Scanner provenance recorded.

**Key specs:** `extraction-and-normalization.md`, `artifact-schemas.md`

## Phase 3: M3 — Graph Construction

**Goal:** Build the global typed atlas graph.

- [x] Implement `scripts/build_risk_graph.py` + tests (T-017)
- [x] Add `make graph` target (T-018)

**Gate:** `graphs/global.graphml` loads cleanly. Package deduplication matches normalized inputs. No `depends_on` edges required.

**Key specs:** `graph-semantics-and-metrics.md`, `artifact-schemas.md`

## Phase 4: M4 — Reporting & Atlas

**Goal:** Produce baseline metrics, rankings, and visualizations.

- [x] Implement `scripts/generate_atlas_reports.py` + tests (T-019)
- [x] Add `make report` and `make all` targets (T-020)

**Gate:** Report outputs validate against schema. Rankings reproducible. No composite risk score.

**Key specs:** `graph-semantics-and-metrics.md`, `artifact-schemas.md`

## Phase 5: Polish, Submission & Showcase

**Goal:** End-to-end validation, final documentation, and a local showcase dashboard for demo use.

- [x] Full pipeline run: `make all` (T-021)
- [x] Cross-phase verification suite (see `PROJECT_CHECKLIST.md`) (T-021)
- [x] Final documentation pass (T-022)
- [x] Ensure all handoff docs reflect final state (T-022)
- [x] Draft dashboard showcase spec and route docs (T-023)
- [x] Implement local Dash/Plotly dashboard + tests (T-024)
- [x] Add `make dashboard` target and demo instructions (T-025)
- [x] Review the live dashboard and lock the redesign roadmap (T-026)
- [x] Create simple LaTeX report scaffold for the final write-up (T-028)
- [x] Dashboard redesign Stage 0: audit and refactor preparation (T-029)
- [x] Dashboard redesign Stage 1: new app shell, layout, and theme (T-030)
- [x] Dashboard redesign Stage 2: branding pass and visual refinement (T-031)
- [ ] Dashboard redesign Stage 3: Cytoscape migration (T-032)
- [ ] Dashboard redesign Stage 4: selection workflow and inspector redesign (T-033)
- [ ] Dashboard redesign Stage 5: filters, search, and linked summary views (T-034)
- [ ] Dashboard redesign Stage 6: final polish for local research use (T-035)

**Gate:** All milestone gates pass. All docs current. Pipeline reproducible end-to-end. Optional showcase dashboard launches locally from the documented artifacts. Post-implementation redesign work follows `docs/dashboard_redesign_plan.md` one stage at a time.
