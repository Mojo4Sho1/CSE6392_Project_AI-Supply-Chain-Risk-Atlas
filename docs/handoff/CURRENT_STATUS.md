# Current Status

**Last updated:** 2026-03-02  
**Owner:** Joe + Codex

## Current focus

Documentation hardening for zero-context agent execution across milestones M1-M4.

## Completed in current focus

- Applied `data/models.csv` schema cutover for human-curated selection metadata:
  - removed ambiguous input columns (`selection_rationale`, `selection_source`, `snapshot_timestamp`, `eligible`)
  - added canonical v1 selection columns (`snapshot_timestamp_utc`, likes/download counts, ranking signal, method, notes)
  - clarified that dependency artifacts and eligibility are runtime-derived during ingestion.
- Added end-to-end master checklist:
  - `docs/handoff/PROJECT_CHECKLIST.md` with phase gates, dependencies, and acceptance criteria for M1-M4.
- Added new authoritative specs:
  - `docs/specs/artifact-schemas.md`
  - `docs/specs/pipeline-execution-contract.md`
  - `docs/specs/testing-and-validation.md`
  - `docs/specs/decision-log.md`
- Updated specs index routing:
  - `docs/specs/_INDEX.md` now includes all active specs and read triggers.
- Resolved policy defaults previously tracked as open decisions:
  - manual curated candidate source (`data/models.csv`) for v1,
  - default sample target of 15,
  - unpinned dependencies map to `vuln_status=unknown`,
  - ambiguous refs resolve to default-branch `HEAD` with provenance,
  - `depends_on` edges deferred in v1,
  - composite risk score out of scope in v1.
- Updated existing specs to align with resolved defaults:
  - `docs/specs/data-sourcing-and-eligibility.md`
  - `docs/specs/extraction-and-normalization.md`
  - `docs/specs/graph-semantics-and-metrics.md`
  - `docs/specs/artifact-schemas.md` (revised `models.json` per-model metadata contract)
- Updated operational docs for consistency:
  - `README.md` now reflects the new `models.csv` schema and curation workflow.
  - `docs/handoff/NEXT_TASK.md` now includes explicit schema/type/enum/timestamp validation requirements for M1 ingestion.

## Passing checks

- All new doc artifacts from the documentation hardening plan are present.
- `docs/specs/_INDEX.md` includes routing entries for every active spec.
- Core policy defaults are now explicit in `docs/specs/decision-log.md`.
- Existing README/spec conflict on ingestion behavior is resolved to artifact-only v1 flow.
- Cross-doc references for `models.csv` are updated to the hard-cutover schema.

## Known gaps/blockers

- No ingestion script implementation exists yet.
- No OSV scan, graph build, or reporting scripts exist yet.
- `data/models.csv` still needs human-populated candidate rows using the new schema columns.

## Active coordination notes

- Documentation baseline is now decision-complete for implementation.
- Next implementation should follow M1 gate requirements from:
  - `docs/handoff/PROJECT_CHECKLIST.md`
  - `docs/specs/artifact-schemas.md`
  - `docs/specs/pipeline-execution-contract.md`

## Next task (single target)

Implement `scripts/ingest_repo_artifacts.py` to produce deterministic per-model manifest outputs from `data/models.csv` using canonical schemas and reason codes.

## Definition of done for next task

- Script exists and follows:
  - `docs/specs/extraction-and-normalization.md`
  - `docs/specs/artifact-schemas.md`
  - `docs/specs/pipeline-execution-contract.md`
- Script emits deterministic `manifests/<model_id>/manifest_index.json` outputs.
- Eligibility pass/fail outcomes use canonical machine-readable reason codes.
- `NEXT_TASK.md` is updated to point to subsequent M2 OSV-scan integration.
