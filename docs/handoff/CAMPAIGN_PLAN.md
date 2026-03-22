# Campaign Plan

**Last updated:** 2026-03-21
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

- Implement `model_id` normalization utility + tests
- Implement CSV parser with v1 schema validation + tests
- Implement artifact discovery with hint support + tests
- Implement eligibility evaluation with canonical reason codes + tests
- Assemble `scripts/ingest_repo_artifacts.py` with CLI contract
- Create `Makefile` with `make ingest` and `make test` targets
- End-to-end M1 smoke test

**Gate:** `manifests/<model_id>/manifest_index.json` produced for all 13 CSV rows. At least one eligible + one ineligible path. All tests pass.

**Key specs:** `artifact-schemas.md`, `pipeline-execution-contract.md`, `data-sourcing-and-eligibility.md`, `extraction-and-normalization.md`, `testing-and-validation.md`

## Phase 2: M2 — OSV Scan & Normalization

**Goal:** Generate raw + normalized vulnerability data for eligible models.

- Install/verify OSV-Scanner availability
- Implement `scripts/run_osv_scan.py` + tests
- Add `make scan` target
- Normalize to `osv/<model_id>/normalized.json` schema

**Gate:** Every eligible model has `raw.json` + `normalized.json`. All normalized files validate against schema. Scanner provenance recorded.

**Key specs:** `extraction-and-normalization.md`, `artifact-schemas.md`

## Phase 3: M3 — Graph Construction

**Goal:** Build the global typed atlas graph.

- Implement `scripts/build_risk_graph.py` + tests
- Add `make graph` target
- Validate graph integrity (node attrs, edge endpoints, deduplication)

**Gate:** `graphs/global.graphml` loads cleanly. Package deduplication matches normalized inputs. No `depends_on` edges required.

**Key specs:** `graph-semantics-and-metrics.md`, `artifact-schemas.md`

## Phase 4: M4 — Reporting & Atlas

**Goal:** Produce baseline metrics, rankings, and visualizations.

- Implement `scripts/generate_atlas_reports.py` + tests
- Add `make report` and `make all` targets
- Generate `reports/summary.json`, `reports/summary.csv`, `figures/`

**Gate:** Report outputs validate against schema. Rankings reproducible. No composite risk score.

**Key specs:** `graph-semantics-and-metrics.md`, `artifact-schemas.md`

## Phase 5: Polish & Submission

**Goal:** End-to-end validation and final documentation.

- Full pipeline run: `make all`
- Cross-phase verification suite (see `PROJECT_CHECKLIST.md`)
- Final documentation pass
- Ensure all handoff docs reflect final state
