# Data Sourcing and Eligibility Spec

## Purpose
Define authoritative rules for sourcing model candidates and determining whether a model repository is eligible for pipeline processing.

## Inputs
- Candidate model list from curated CSV (`data/models.csv`) in v1.
- Required CSV columns:
  - `hf_model_id`
  - `source_repo_url`
  - `snapshot_timestamp_utc`
  - `hf_downloads_at_snapshot` (non-negative integer)
  - `hf_likes_at_snapshot` (non-negative integer; human-readable shorthand like "2.59k" accepted, normalized during ingestion)
- Optional CSV columns:
  - `dependency_artifact` (human-curated hint for artifact filename/path)
  - `dependency_artifact_url` (direct URL to the artifact in the source repo)
  - `selection_rationale` (freeform text explaining why this model was selected)
  - `curation_notes` (freeform operator notes)

## Authoritative Rules

### Candidate Source of Truth
- In v1, `data/models.csv` is authoritative for candidate selection.
- `data/models.csv` rows are human-owned and human-approved in v1.
- Each row in `data/models.csv` represents a final selected model candidate for ingestion.
- `hf_model_id` and `source_repo_url` are required; rows missing either are invalid.
- Candidate target size default is 15 models unless handoff docs explicitly override.
- `dependency_artifact` and `dependency_artifact_url` are optional human-curated hints in the CSV. When present, the ingestion script uses them as a starting point but may discover additional artifacts at runtime.
- Eligibility is determined at runtime and recorded in output artifacts.

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
