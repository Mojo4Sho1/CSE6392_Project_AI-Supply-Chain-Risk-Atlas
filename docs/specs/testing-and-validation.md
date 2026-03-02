# Testing and Validation Spec

## Purpose
Define required test coverage, milestone validation gates, and reproducibility checks for the pipeline.

## Test Layers

### Unit tests (required)

Coverage expectations:

- `model_id` normalization is deterministic and collision-resistant.
- `models.csv` header contract validation enforces the exact v1 schema (no legacy aliases).
- CSV required-field validation maps failures to canonical reason codes.
- `hf_likes_at_snapshot` and `hf_downloads_at_snapshot` validate as non-negative integers.
- `snapshot_timestamp_utc` validates as UTC `Z`-suffix timestamp.
- `ranking_signal` and `selection_method` validate against allowed enums.
- Eligibility reason-code mapping is stable and complete.
- Schema serialization helper behavior is deterministic.
- `vuln_status` handling for unpinned versions always returns `unknown` in v1.

### Integration tests (required)

Coverage expectations:

- Ingestion script produces valid `manifest_index.json` for eligible and ineligible rows.
- OSV normalization produces valid `normalized.json` with required provenance/scanner fields.
- Graph build consumes normalized outputs and emits valid `graphs/global.graphml`.
- Reporting script emits `reports/summary.json` and `reports/summary.csv` with required metrics.

### End-to-end smoke tests (required)

Coverage expectations:

- Run M1-M4 in sequence on a small fixture set.
- Verify contracts at each output boundary.
- Confirm outputs are generated in expected directories.

### Documentation consistency checks (required)

Coverage expectations:

- `docs/specs/_INDEX.md` includes all active spec files.
- No unresolved `OPEN_DECISION` markers remain in active v1 specs.
- README policy statements do not contradict active specs.

## Fixture Requirements

Fixtures must include at least:

- one row that should pass eligibility,
- one row with legacy header fields that should fail input-contract validation,
- one row that should fail `ERR_REPO_UNREACHABLE`,
- one row that should fail `ERR_NO_SUPPORTED_ARTIFACTS`,
- one row that should fail `ERR_ARTIFACT_PARSE_FAILED`.

Fixture guidance:

- Keep fixtures small and deterministic.
- Prefer mocked repo/artifact resolution for unit/integration tests.
- Keep expected outputs versioned with schema version under test.

## Milestone Validation Gates

### M1 gate

- Script-level validation:
  - `python scripts/ingest_repo_artifacts.py --help` exits 0.
- Output validation:
  - all manifest outputs validate against schema.
- Behavioral validation:
  - at least one eligible and one ineligible reason-path observed.

### M2 gate

- Script-level validation:
  - `python scripts/run_osv_scan.py --help` exits 0.
- Output validation:
  - each eligible model has paired raw + normalized outputs.
  - normalized files validate against schema and enums.

### M3 gate

- Script-level validation:
  - `python scripts/build_risk_graph.py --help` exits 0.
- Output validation:
  - global graph exists and loads.
- Behavioral validation:
  - package dedup and per-model edge counts align with normalized inputs.

### M4 gate

- Script-level validation:
  - `python scripts/generate_atlas_reports.py --help` exits 0.
- Output validation:
  - summary JSON/CSV outputs exist and validate required fields.
- Behavioral validation:
  - baseline metric values are reproducible for identical inputs.

## Determinism and Reproducibility Requirements

- Re-run same command with same inputs:
  - outputs must match byte-for-byte except allowed timestamp fields.
- Deterministic sorting must be applied to:
  - candidate processing order,
  - package arrays,
  - vulnerability ID arrays,
  - report ranking tie-breaks.

## Negative-Path Assertions

- Unreachable repo maps to `ERR_REPO_UNREACHABLE`.
- Missing recognized artifacts maps to `ERR_NO_SUPPORTED_ARTIFACTS`.
- Artifact parser fatal error maps to `ERR_ARTIFACT_PARSE_FAILED`.
- Reason codes must not be substituted with ad-hoc values.

## Suggested Validation Commands

- `pytest -q`
- `rg -n "OPEN_DECISION" docs/specs README.md docs/handoff --glob '!docs/specs/testing-and-validation.md'`
- `rg -n "reason_code|schema_version|generated_at_utc" manifests osv reports`

## Failure Policy

- Fail fast on schema contract violations.
- Do not fail on expected candidate ineligibility outcomes.
- Treat undocumented reason codes as test failures.
