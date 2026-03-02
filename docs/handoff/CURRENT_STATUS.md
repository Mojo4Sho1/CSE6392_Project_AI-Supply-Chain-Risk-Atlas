# Current Status

**Last updated:** 2026-03-02  
**Owner:** Joe + Codex

## Current focus

Documentation hardening for zero-context agent execution across milestones M1-M4.

## Completed in current focus

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
- Updated operational docs for consistency:
  - `README.md` now reflects artifact-only ingestion and v1 policy defaults.
  - `AGENTS.md` now includes a new-agent bootstrap checklist.
  - `docs/handoff/NEXT_TASK.md` now points to the next executable M1 implementation batch.

## Passing checks

- All new doc artifacts from the documentation hardening plan are present.
- `docs/specs/_INDEX.md` includes routing entries for every active spec.
- Core policy defaults are now explicit in `docs/specs/decision-log.md`.
- Existing README/spec conflict on ingestion behavior is resolved to artifact-only v1 flow.

## Known gaps/blockers

- No ingestion script implementation exists yet.
- No OSV scan, graph build, or reporting scripts exist yet.
- `data/models.csv` still needs human-populated candidate rows for full run execution.

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
