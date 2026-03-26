# Project Checklist

**Last updated:** 2026-03-26  
**Owner:** Joe + Codex

## Purpose

Provide a decision-complete, end-to-end execution checklist for milestones M1-M5.  
`docs/handoff/NEXT_TASK.md` remains the source of truth for the immediate batch.  
This file is the long-horizon control document for zero-context agents.

## Locked v1 Defaults

- `data/models.csv` rows are human-owned and human-approved.
- Candidate generation policy is manual curation in `data/models.csv`.
- Default target sample size is 15 models (within project range 10-20).
- Unpinned dependencies must map to `vuln_status=unknown`.
- Ambiguous repository refs resolve to default-branch `HEAD` with provenance.
- Required v1 graph edge type is `uses_package`; `depends_on` is deferred.
- Composite risk score is out of scope for v1; baseline metrics only.

## Global Preconditions

- Environment:
  - `conda env create -f environment.yml`
  - `conda activate ai-supply-chain-risk-atlas`
- Input source:
  - `data/models.csv` is authoritative for v1 candidate intake.
  - rows are final selected candidates only; no rejected rows are tracked in this file.
  - dependency artifact types and eligibility are runtime-derived, not human-entered CSV fields.
- Determinism:
  - iterate candidates in stable sorted order,
  - serialize JSON with stable key ordering,
  - write outputs atomically,
  - keep all timestamps in UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- Contracts:
  - schema and enum contracts in `docs/specs/artifact-schemas.md`,
  - CLI and runtime contracts in `docs/specs/pipeline-execution-contract.md`.

## Milestone Gates

### Phase 5: Validation and Documentation

**Objective**  
Validate the completed M1-M4 pipeline end-to-end from the repository root and reconcile project documentation with the implemented v1 behavior.

**Required inputs**
- Existing M1-M4 artifacts under `manifests/`, `osv/`, `graphs/`, `reports/`, and `figures/`
- `README.md`
- `docs/handoff/*`
- `docs/specs/testing-and-validation.md`
- `docs/specs/pipeline-execution-contract.md`
- `docs/specs/artifact-schemas.md`

**Checklist**
- [x] Run the script-level smoke checks for all M1-M4 CLIs (`--help` exits 0).
- [x] Run `make all` from repo root.
- [x] Run `make test` from repo root.
- [x] Reconcile README, handoff docs, and spec routing with the implemented v1 pipeline.
- [x] Record local cross-phase verification outcomes and any caveats.

**Acceptance gate**
- [x] No stale `models.json` references remain in active README/spec/handoff docs.
- [x] README, specs, and handoff docs express one artifact-only ingestion policy and one required v1 graph edge policy (`uses_package`, with `depends_on` deferred).
- [x] The post-validation backlog is narrowed to the optional dashboard showcase and redesign track.

### Phase 5B: Showcase Dashboard

**Objective**  
Implement and verify the optional local dashboard as a read-only presentation layer over the completed M1-M4 artifacts.

**Required inputs**
- `graphs/global.graphml`
- `reports/summary.json`
- `reports/summary.csv`
- `docs/specs/dashboard-showcase.md`
- `environment.yml`

**Checklist**
- [x] Add the dashboard runtime dependencies to `environment.yml`.
- [x] Implement the dashboard data/view/render/app split with a Plotly renderer seam.
- [x] Add `scripts/run_dashboard.py` and `make dashboard`.
- [x] Add automated tests for dashboard loaders, view logic, renderer behavior, and startup.
- [x] Update README/spec/handoff docs for the local dashboard launch flow and future renderer seam.

**Acceptance gate**
- [x] `python scripts/run_dashboard.py --help` exits 0.
- [x] `make test` passes after the dashboard additions.
- [x] `make validate` passes after the dashboard additions.
- [x] `make dashboard` launches locally on `127.0.0.1:8050` with the documented defaults.
- [x] The renderer seam is explicit enough that a future Cytoscape renderer can reuse the same data/view-model layer.

**Post-gate refinement note**
- Future dashboard redesign work is governed by `docs/dashboard_redesign_plan.md`.
- Implement one redesign stage per batch; do not combine major stages.
- Keep Plotly in place through Stages 0-2 and defer Cytoscape migration to Stage 3.
- Stage 0 redesign preparation is complete: theme tokens, layout/controller seams, repo `assets/` wiring, and a reserved branding asset home now exist so Stage 1 can focus on the shell and theme work directly.
- Stage 1 redesign shell is complete: the dashboard now uses a top bar / left sidebar / center graph / right inspector shell with a dark application chrome and a light Plotly graph canvas, so Stage 2 can focus on branding polish rather than layout restructuring.
- Stage 2 branding pass is complete: the in-shell legend now lives alongside the graph, package vulnerability IDs in the inspector open OSV advisories directly, and the no-logo shell polish is complete enough for Stage 3 to focus on the Cytoscape renderer migration rather than revisiting Stage 2 presentation work.

### M1: Ingestion and Eligibility Baseline

**Objective**  
Build deterministic artifact-ingestion outputs from `data/models.csv` under strict eligibility policy.

**Required inputs**
- `data/models.csv`
- `docs/specs/data-sourcing-and-eligibility.md`
- `docs/specs/extraction-and-normalization.md`
- `docs/specs/artifact-schemas.md`
- `docs/specs/pipeline-execution-contract.md`

**Required outputs**
- `manifests/<model_id>/manifest_index.json` for every candidate row
- Optional run-level logs for diagnostics

**Checklist**
- [x] Implement ingestion script contract.
- [x] Enforce required CSV fields and strict eligibility checks.
- [x] Validate CSV header as exact hard-cutover v1 schema.
- [x] Validate snapshot/metric/enum input constraints from schema spec.
- [x] Discover dependency artifacts at runtime from repository sources.
- [x] Emit canonical eligibility `reason_code` values.
- [x] Capture provenance (`source_repo_url`, resolved ref, commit SHA or unknown reason, evaluation timestamp).
- [x] Guarantee deterministic output formatting and ordering.

**Acceptance gate**
- [x] At least one eligible and one ineligible path represented in outputs (fixtures or real rows).
- [x] All manifest files validate against the v1 manifest schema.
- [x] No undocumented reason codes are emitted.
- [x] Legacy CSV schema variants fail with explicit input-contract errors.

### M2: OSV Scan and Normalization

**Objective**  
Generate raw OSV results and normalized vulnerability data for all eligible models.

**Required inputs**
- Eligible `manifest_index.json` outputs from M1
- OSV scanner available in runtime environment
- `docs/specs/extraction-and-normalization.md`
- `docs/specs/artifact-schemas.md`

**Required outputs**
- `osv/<model_id>/raw.json`
- `osv/<model_id>/normalized.json`

**Checklist**
- [x] Scan only eligible candidates from M1 outputs.
- [x] Persist raw scanner output unchanged when OSV-Scanner emits JSON; emit deterministic empty results when an eligible artifact declares no scanable packages.
- [x] Normalize to schema version `1.0`.
- [x] Set `vuln_status=unknown` for unpinned versions.
- [x] Keep package identity invariant `(ecosystem, name, version)`.

**Acceptance gate**
- [x] Every raw output has a paired normalized output.
- [x] Normalized files validate against schema and enum contracts.
- [x] Scanner name/version and provenance are present in each normalized file.

### M3: Graph Build and Validation

**Objective**  
Construct global typed atlas graph and validate semantic correctness.

**Required inputs**
- `osv/<model_id>/normalized.json` for scanned models
- `docs/specs/graph-semantics-and-metrics.md`
- `docs/specs/artifact-schemas.md`

**Required outputs**
- `graphs/global.graphml`
- Optional: `graphs/per_model/<model_id>.graphml`

**Checklist**
- [x] Build `Model` and `Package` nodes with required attributes.
- [x] Build `uses_package` edges with required attributes.
- [x] Deduplicate packages strictly by `(ecosystem, name, version)`.
- [x] Enforce graph integrity checks (edge endpoints exist, required attrs present).

**Acceptance gate**
- [x] Global graph loads without schema/typing errors.
- [x] Package deduplication and per-model counts match normalized inputs.
- [x] Deferred `depends_on` edges are not required for v1 completion.

### M4: Reporting and Atlas Outputs

**Objective**  
Produce baseline metrics/rankings and final report artifacts from the graph.

**Required inputs**
- `graphs/global.graphml`
- `docs/specs/graph-semantics-and-metrics.md`
- `docs/specs/artifact-schemas.md`

**Required outputs**
- `reports/summary.json`
- `reports/summary.csv`
- `figures/` visual outputs

**Checklist**
- [x] Compute baseline dependency, vulnerability, and risk-structure metrics.
- [x] Emit per-model and aggregate metrics with stable ordering.
- [x] Generate reproducible figures from the same graph input.

**Acceptance gate**
- [x] Report outputs validate against schema contracts.
- [x] Rankings are reproducible for identical inputs.
- [x] Composite risk score is absent unless the decision log is explicitly revised.

## Cross-Phase Verification Suite

Validation status for this repository snapshot (`2026-03-26`):

- Routing test:
  - passed; the required read order plus rewritten handoff files now point cleanly to the staged dashboard redesign track anchored by `docs/dashboard_redesign_plan.md`.
- Contract test:
  - partially covered by the existing schema-contract unit/integration suite; the repo does not maintain a second independent implementation for direct output comparison.
- Determinism test:
  - passed for the staged validation path; `make all` completes cleanly with unchanged inputs, and regenerated artifacts are expected to vary only in allowed timestamp fields.
- Negative-path test:
  - passed via the existing automated test suite (`make test`), which covers unreachable repo, missing artifacts, and parse-failure reason-code mapping.
- Cross-document consistency test:
  - passed after removing stale `data/models.json` references and reconciling README/spec routing with the implemented artifact-only M1-M4 pipeline.
- Handoff continuity test:
  - passed; `CURRENT_STATUS.md` and `NEXT_TASK.md` were rewritten in the required format without introducing new policy assumptions.
- Showcase dashboard test:
  - passed; the Plotly dashboard still reads the live graph/report artifacts at startup after the Stage 1 shell redesign. In this workstation snapshot, `make dashboard` hit an external port-8050 conflict after the startup banner, so launch was additionally verified on `127.0.0.1:8060`.
- Dashboard redesign preparation test:
  - passed; `dashboard_theme.py`, `dashboard_controller.py`, `dashboard_layout.py`, and `assets/branding/` now provide the explicit seams and asset home expected by `docs/dashboard_redesign_plan.md` Stage 0.
- Dashboard Stage 1 shell test:
  - passed; the app layout now exposes the expected graph-first shell regions (top bar, left sidebar, center graph, right inspector) and the Plotly renderer uses dedicated light-canvas text tokens so labels remain readable inside the new shell.
- Dashboard Stage 2 branding test:
  - passed; the graph now uses a compact in-shell legend, the package inspector renders external OSV advisory links, the default no-logo direction remains intact, and dashboard verification still passed with the existing live graph/report artifacts.

## Handoff Obligations Per Batch

- Update `docs/handoff/PROJECT_CHECKLIST.md` when the completed batch changes milestone checklist status, acceptance-gate status, or cross-phase verification readiness.
- Update `docs/handoff/CURRENT_STATUS.md` with:
  - concrete completed work,
  - checks run and outcomes,
  - remaining blockers.
- Update `docs/handoff/NEXT_TASK.md` with:
  - one executable next batch,
  - explicit in-scope/out-of-scope,
  - acceptance criteria and verification steps.
- If no checklist item changed in the batch, explicitly confirm that no `PROJECT_CHECKLIST.md` state changed before closing the task.
- If specs changed:
  - update `docs/specs/_INDEX.md` in the same commit.

## Change Control

- If implementation needs behavior not covered by current specs, add/update spec first.
- If changing locked defaults, update:
  - `docs/specs/decision-log.md`,
  - impacted specs,
  - README statements that reference the changed policy.
