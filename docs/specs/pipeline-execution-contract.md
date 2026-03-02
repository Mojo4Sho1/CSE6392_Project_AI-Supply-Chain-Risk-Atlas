# Pipeline Execution Contract Spec

## Purpose
Define script boundaries, CLI contracts, runtime behavior, and determinism requirements for pipeline execution.

## Scope

- This spec governs runtime behavior for milestone scripts.
- Artifact field-level schemas are defined in `docs/specs/artifact-schemas.md`.

## Canonical Script Boundaries (v1)

### 1) Ingestion and eligibility

- Script: `scripts/ingest_repo_artifacts.py`
- Responsibility:
  - read `data/models.csv`,
  - resolve repository reference and commit provenance,
  - discover recognized dependency artifacts,
  - evaluate strict eligibility,
  - write `manifests/<model_id>/manifest_index.json`.

### 2) OSV scan and normalization

- Script: `scripts/run_osv_scan.py`
- Responsibility:
  - scan eligible artifacts,
  - write `osv/<model_id>/raw.json`,
  - normalize to `osv/<model_id>/normalized.json`.

### 3) Graph build

- Script: `scripts/build_risk_graph.py`
- Responsibility:
  - read normalized outputs,
  - build `graphs/global.graphml`,
  - optionally emit per-model subgraphs.

### 4) Reporting

- Script: `scripts/generate_atlas_reports.py`
- Responsibility:
  - compute required metrics,
  - write `reports/summary.json` and `reports/summary.csv`,
  - generate figures.

## Common CLI Contract

All milestone scripts must expose these options:

- `--input` (path; required)
- `--output-root` (path; required)
- `--snapshot-timestamp` (UTC timestamp; required)
- `--dry-run` (flag; optional)
- `--log-level` (`DEBUG|INFO|WARNING|ERROR`; optional, default `INFO`)

Stage-specific options are allowed, but they must not redefine common option semantics.

## Exit Code Contract

- `0`: run completed; expected per-model ineligible outcomes are allowed.
- `2`: input contract violation (schema, required fields, invalid timestamp).
- `3`: required external dependency unavailable (for example OSV scanner missing).
- `4`: unrecoverable runtime failure (cannot complete run contract).

## Runtime Behavior Requirements

### Deterministic ordering

- Process candidate rows ordered by:
  1. `hf_model_id` ascending
  2. original input row number ascending (tie-break)
- Sort all emitted arrays that have no semantic ordering requirement.

### Idempotent output writes

- Each run must fully determine final output state from inputs.
- Writes must use temp-file then atomic rename behavior.
- Existing output files for the same target may be overwritten, but content must be deterministic.

### Timestamp and timezone

- All generated timestamps must be UTC with `Z` suffix.
- Local timezone offsets must not be written into output artifacts.

### JSON serialization

- UTF-8
- stable key ordering
- indentation of 2 spaces
- trailing newline

## Retry and Error Policy

### Transient operation retries

- Retry transient network/tool operations up to 3 attempts.
- Backoff schedule: `1s`, `2s`, `4s`.
- Log each retry attempt with operation context.

### Non-transient handling

- Input row errors, unsupported artifacts, parse failures, and explicit eligibility failures are not retried.
- They must map to canonical `eligibility_reason_code` values.

### Partial failure handling

- Expected ineligible outcomes are represented in outputs and do not fail the full run.
- Unexpected internal failures that prevent output contract completion must return exit code `4`.

## Ingestion Policy (v1)

- Artifact acquisition mode is `artifact_only` by default.
- Full repository clone is not part of v1 automated contract.
- Commit/ref resolution strategy:
  - use requested ref if supplied and valid,
  - otherwise resolve default branch `HEAD`,
  - always record strategy and resolution provenance in manifest output.

## Observability Requirements

- At script start, log:
  - script name/version,
  - input path,
  - output root,
  - snapshot timestamp,
  - dry-run state.
- For each candidate, log:
  - `hf_model_id`,
  - resolved `model_id`,
  - eligibility outcome,
  - reason code when ineligible.

## Compatibility and Change Rules

- Changes to common CLI flags are breaking changes.
- Breaking runtime contract changes require:
  - schema/spec updates,
  - handoff update,
  - explicit note in decision log when policy behavior changes.
