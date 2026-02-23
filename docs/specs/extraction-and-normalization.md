# Extraction and Normalization Spec

## Purpose
Define the contract for repository artifact extraction, OSV scan execution, and normalized vulnerability output schema.

## Pipeline Stages

1. Candidate intake from `data/models.csv`.
2. Repository artifact acquisition.
3. OSV scan execution on acquired artifacts.
4. Normalization into stable JSON schema under `osv/<model_id>/normalized.json`.

## Repository Artifact Acquisition Contract

### Goal
Acquire only required dependency artifacts and minimal provenance metadata, without full repository cloning by default.

### Contract (No Implementation in this Spec)
A future ingestion script (e.g., `scripts/ingest_repo_artifacts.py`) must:

- Input:
  - `hf_model_id`
  - `source_repo_url`
  - optional commit SHA or ref
- Behavior:
  - Discover and fetch dependency-related files only.
  - Record provenance metadata (repo URL, resolved commit/ref, fetch timestamp).
  - Record acquisition outcome and exclusion reason if strict eligibility fails.
- Output:
  - `manifests/<model_id>/manifest_index.json`
  - optional local artifact cache for scanner input

### Non-Goals for v1
- Full generic repo mirroring.
- Heuristic scraping outside standard repo file APIs/workflows.

## OSV Output Requirements
For each eligible model:
- Persist raw output to `osv/<model_id>/raw.json`.
- Normalize to `osv/<model_id>/normalized.json`.

## Normalized Schema (minimum required fields)
Top-level:
- `schema_version` (string; start with `1.0`)
- `generated_at` (ISO timestamp)
- `hf_model_id`
- `source_repo_url`
- `repo_commit_sha` (or `unknown` with reason)
- `scanner`
  - `name`
  - `version`
- `packages` (array)

Per package entry:
- `ecosystem`
- `name`
- `version` (string or `null`)
- `dependency_scope` (`direct` | `transitive` | `unknown`)
- `manifest_source` (path or `unknown`)
- `vuln_status`
- `vuln_ids` (array)
- `max_severity_bucket` (`LOW` | `MEDIUM` | `HIGH` | `CRITICAL` | `UNKNOWN`)
- `fix_available` (boolean)

## Invariants
- Raw and normalized outputs must be generated together for traceability.
- `schema_version` must be present on all normalized outputs.
- Package identity for downstream graphing is `(ecosystem, name, version)`.

## Open Decisions
- `OPEN_DECISION`: unpinned dependency policy for `vuln_status` (`unknown` only vs `potentially_vulnerable`).
- `OPEN_DECISION`: default strategy for commit resolution when repo refs are ambiguous.
