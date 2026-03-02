# Artifact Schemas Spec

## Purpose
Define authoritative schema contracts and enums for versioned project artifacts.

## Conventions

- All schema versions in this doc start at `1.0`.
- All timestamps must be UTC ISO-8601 with `Z` suffix (`YYYY-MM-DDTHH:MM:SSZ`).
- All JSON output files must be serialized with:
  - UTF-8 encoding,
  - stable key ordering,
  - trailing newline.
- `model_id` is a filesystem-safe deterministic derivative of `hf_model_id`.

## Canonical Enums

### `eligibility_reason_code`

- `OK_ELIGIBLE`
- `ERR_INPUT_MISSING_REQUIRED_FIELD`
- `ERR_INPUT_INVALID_TIMESTAMP`
- `ERR_REPO_UNREACHABLE`
- `ERR_REPO_FORBIDDEN`
- `ERR_REF_RESOLUTION_FAILED`
- `ERR_NO_SUPPORTED_ARTIFACTS`
- `ERR_ARTIFACT_FETCH_FAILED`
- `ERR_ARTIFACT_PARSE_FAILED`
- `ERR_MODEL_ARTIFACT_MAPPING_AMBIGUOUS`

### `dependency_scope`

- `direct`
- `transitive`
- `unknown`

### `vuln_status` (v1)

- `vulnerable`
- `not_vulnerable`
- `unknown`

### `severity_bucket`

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`
- `UNKNOWN`

## Deterministic `model_id` Normalization

Given `hf_model_id`:

1. lowercase the original string
2. replace `/` with `--`
3. replace each character outside `[a-z0-9._-]` with `-`
4. collapse repeated `-` to single `-`
5. trim leading/trailing `-`
6. if empty, use slug `model`
7. append `--` plus first 8 hex chars of SHA-1 over the original `hf_model_id`

Output format:
- `<slug>--<hash8>`

Rationale:
- readable path,
- deterministic collision resistance.

## Schema: `data/models.json`

### Required top-level fields

- `schema_version` (string, must be `1.0`)
- `snapshot_timestamp_utc` (timestamp)
- `selection_policy` (string; v1 default `manual_curated_csv_v1`)
- `target_sample_size` (integer; v1 default `15`)
- `source_csv` (string; expected `data/models.csv`)
- `models` (array)

### Required per-model fields

- `hf_model_id` (string)
- `model_id` (string)
- `source_repo_url` (string)
- `selection_rationale` (string)
- `selection_source` (string)
- `snapshot_timestamp` (timestamp)
- `eligible` (boolean)
- `repo_commit_sha` (string; SHA or `unknown`)
- `dependency_artifacts_found` (array of strings; may be empty)

## Schema: `manifests/<model_id>/manifest_index.json`

### Required top-level fields

- `schema_version` (string, `1.0`)
- `generated_at_utc` (timestamp)
- `hf_model_id` (string)
- `model_id` (string)
- `source_repo_url` (string)
- `snapshot_timestamp` (timestamp copied from input row)
- `resolved_reference` (object)
- `artifact_fetch` (object)
- `eligibility` (object)
- `provenance` (object)

### Required `resolved_reference` fields

- `requested_ref` (string; `default` if none provided)
- `resolution_strategy` (string; v1 default `default_branch_head`)
- `resolved_ref` (string)
- `repo_commit_sha` (string; SHA or `unknown`)
- `repo_commit_sha_reason` (string; `none` when SHA known)

### Required `artifact_fetch` fields

- `mode` (string; v1 default `artifact_only`)
- `recognized_artifacts` (array of artifact names considered)
- `artifacts_found` (array of objects)
- `artifact_parse_failures` (array of objects, may be empty)

Each `artifacts_found` item:
- `path` (string)
- `ecosystem` (string)
- `artifact_type` (string)
- `parse_status` (`parsed` or `not_parsed`)

Each `artifact_parse_failures` item:
- `path` (string)
- `error_code` (string)
- `error_detail` (string)

### Required `eligibility` fields

- `eligible` (boolean)
- `reason_code` (`eligibility_reason_code`)
- `reason_detail` (string; machine-readable primary detail)

### Required `provenance` fields

- `input_file` (string)
- `input_row_number` (integer, 1-based data row index)
- `runner` (string; script name)
- `runner_version` (string)

## Schema: `osv/<model_id>/normalized.json`

### Required top-level fields

- `schema_version` (string, `1.0`)
- `generated_at_utc` (timestamp)
- `hf_model_id` (string)
- `model_id` (string)
- `source_repo_url` (string)
- `repo_commit_sha` (string; SHA or `unknown`)
- `repo_commit_sha_reason` (string; `none` when SHA known)
- `scanner` (object with `name` and `version`)
- `packages` (array)

### Required per-package fields

- `ecosystem` (string)
- `name` (string)
- `version` (string or `null`)
- `dependency_scope` (`dependency_scope`)
- `manifest_source` (string or `unknown`)
- `vuln_status` (`vuln_status`)
- `vuln_ids` (array of strings, unique, sorted)
- `num_vulns` (integer)
- `max_severity_bucket` (`severity_bucket`)
- `fix_available` (boolean)

Rules:
- package identity is `(ecosystem, name, version)`,
- for unpinned dependencies in v1, set `vuln_status=unknown`.

## Schema: `reports/summary.json`

### Required top-level fields

- `schema_version` (string, `1.0`)
- `generated_at_utc` (timestamp)
- `snapshot_timestamp_utc` (timestamp)
- `graph_source` (string path)
- `global_metrics` (object)
- `per_model_metrics` (array)
- `reused_vulnerable_packages` (array)

### Required `global_metrics` fields

- `unique_package_count` (integer)
- `average_packages_per_model` (number)
- `average_direct_packages_per_model` (number)
- `average_transitive_packages_per_model` (number)

### Required `per_model_metrics` item fields

- `hf_model_id` (string)
- `model_id` (string)
- `vulnerable_direct_dependencies` (integer)
- `vulnerable_transitive_dependencies` (integer)
- `vulnerable_packages_per_model` (integer)
- `unique_vuln_ids_per_model` (integer)

### Required `reused_vulnerable_packages` item fields

- `ecosystem` (string)
- `name` (string)
- `version` (string or `null`)
- `impacted_model_count` (integer)
- `vuln_ids` (array of strings)

## Schema Evolution Rules

- Backward-incompatible changes must increment major schema version.
- Additive fields that preserve compatibility may increment minor version.
- Any schema change requires synchronized updates to:
  - this file,
  - `docs/specs/_INDEX.md`,
  - impacted producer/consumer scripts,
  - handoff docs if the active task depends on changed fields.
