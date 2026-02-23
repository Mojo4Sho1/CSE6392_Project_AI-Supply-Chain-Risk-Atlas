# Data Sourcing and Eligibility Spec

## Purpose
Define authoritative rules for sourcing model candidates and determining whether a model repository is eligible for pipeline processing.

## Inputs
- Candidate model list from either:
  - curated CSV (`data/models.csv`), or
  - future automated Hugging Face query workflow.
- Minimum CSV columns:
  - `hf_model_id`
  - `source_repo_url`
  - `selection_rationale`
  - `selection_source`
  - `snapshot_timestamp`
  - `eligible`

## Authoritative Rules

### Candidate Source of Truth
- During early project phases, `data/models.csv` is authoritative for candidate selection.
- `hf_model_id` and `source_repo_url` are required; rows missing either are invalid.

### Eligibility Policy (Strict by Default)
A candidate is eligible only if all checks pass:

1. Repository is publicly reachable.
2. Repository has at least one recognized dependency artifact.
3. Dependency artifact set is readable by tooling (no parse-fatal corruption).
4. Repo layout allows unambiguous mapping between model and dependency artifacts.

If any check fails, set `eligible=false` and record exclusion reason in processing metadata.

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

## Open Decisions
- `OPEN_DECISION`: automated candidate generation policy (likes/downloads/hybrid) and tie-break strategy.
- `OPEN_DECISION`: final sample-size target within 10-20 and potential modality stratification.
