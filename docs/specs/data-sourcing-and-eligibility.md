# Data Sourcing and Eligibility Spec

## Purpose
Define authoritative rules for sourcing model candidates and determining whether a model repository is eligible for pipeline processing.

## Inputs
- Candidate model list from curated CSV (`data/models.csv`) in v1.
- Minimum CSV columns:
  - `hf_model_id`
  - `source_repo_url`
  - `selection_rationale`
  - `selection_source`
  - `snapshot_timestamp`
  - `eligible`

## Authoritative Rules

### Candidate Source of Truth
- In v1, `data/models.csv` is authoritative for candidate selection.
- `data/models.csv` rows are human-owned and human-approved in v1.
- `hf_model_id` and `source_repo_url` are required; rows missing either are invalid.
- Candidate target size default is 15 models unless handoff docs explicitly override.

### Eligibility Policy (Strict by Default)
A candidate is eligible only if all checks pass:

1. Repository is publicly reachable.
2. Repository has at least one recognized dependency artifact.
3. Dependency artifact set is readable by tooling (no parse-fatal corruption).
4. Repo layout allows unambiguous mapping between model and dependency artifacts.

If any check fails, set `eligible=false` and record exclusion reason in processing metadata.

Eligibility reason codes must come from `docs/specs/artifact-schemas.md`.

### Recognized Dependency Artifacts (initial)
- Python: `requirements.txt`, `pyproject.toml`, `poetry.lock`, `Pipfile`, `Pipfile.lock`
- JavaScript/Node: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- Additional ecosystems may be added later via spec update.

## Outputs
- A filtered eligible model set for ingestion.
- A reproducible eligibility decision log per candidate (file path and format defined in extraction spec).

## Invariants
- Eligibility decisions are deterministic for a fixed repo commit and fixed artifact parser version.
- Exclusions are explicit and auditable.
- No silent skipping of invalid or unreachable repositories.

## Resolved Defaults for v1
- Candidate generation is manual curation via `data/models.csv`.
- Default sample target is 15 models.
- Automated ranking policy is deferred.

Decision authority: `docs/specs/decision-log.md`.
