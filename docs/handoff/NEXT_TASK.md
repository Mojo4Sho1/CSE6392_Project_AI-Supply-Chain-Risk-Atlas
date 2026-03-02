# Next Task

**Last updated:** 2026-03-02  
**Owner:** Joe + Codex

## Task summary

Implement M1 ingestion and eligibility baseline as the first executable batch under the new decision-complete contracts, using `data/models.csv` as input and producing deterministic `manifests/<model_id>/manifest_index.json` outputs.

## Why this task is next

- End-to-end governance and milestone gates now exist in `docs/handoff/PROJECT_CHECKLIST.md`.
- Policy defaults and schema contracts are now resolved in specs.
- The highest-priority remaining gap is turning M1 docs into runnable ingestion code.

Long-horizon reference:
- `docs/handoff/PROJECT_CHECKLIST.md` (full M1-M4 execution runway)

## Scope (in)

- Implement `scripts/ingest_repo_artifacts.py` that:
  - reads `data/models.csv`,
  - validates required fields,
  - evaluates strict eligibility checks,
  - writes per-model manifest index/outcome metadata under `manifests/<model_id>/`.
- Enforce canonical `eligibility_reason_code` values from `docs/specs/artifact-schemas.md`.
- Implement deterministic `model_id` normalization contract from `docs/specs/artifact-schemas.md`.
- Ensure manifest output matches `manifests/<model_id>/manifest_index.json` schema contract.
- Add short run instructions in script docstring and README if needed.

## Scope (out)

- Full OSV scan integration.
- Graph construction and reporting.
- Automated Hugging Face ranking/selection policy.

## Dependencies / prerequisites

- Environment + workflow:
  - `environment.yml`
  - `AGENTS.md`
  - `docs/handoff/PROJECT_CHECKLIST.md`
- Data and specs:
  - `data/models.csv`
  - `docs/specs/data-sourcing-and-eligibility.md`
  - `docs/specs/extraction-and-normalization.md`
  - `docs/specs/artifact-schemas.md`
  - `docs/specs/pipeline-execution-contract.md`
  - `docs/specs/testing-and-validation.md`
  - `docs/specs/decision-log.md`
- Routing:
  - `docs/specs/_INDEX.md`

## Implementation notes

- Keep implementation minimal and deterministic.
- Treat strict eligibility failures as expected outcomes, not hard crashes.
- Keep reason codes stable and machine-readable for downstream analysis.

## Subtasks

- [ ] Create `scripts/ingest_repo_artifacts.py` with required common CLI contract flags.
- [ ] Implement canonical `model_id` normalization.
- [ ] Implement strict eligibility checks and canonical reason-code mapping.
- [ ] Emit deterministic manifest JSON files under `manifests/<model_id>/`.
- [ ] Add/execute tests for at least one eligible and one ineligible path.
- [ ] Update handoff docs after implementation outcomes.

## Acceptance criteria (definition of done)

- Script runs from shared conda env and processes `data/models.csv` end-to-end.
- Manifest outputs conform to v1 schema and enum contracts.
- At least one successful and one failed eligibility path are represented in output metadata.
- Output files are deterministic and reproducible for same inputs.
- Handoff docs are updated with outcomes and next M2 OSV-scan task.

## Verification checklist

- [ ] `python scripts/ingest_repo_artifacts.py --help` works.
- [ ] Running script against `data/models.csv` produces `manifests/<model_id>/manifest_index.json` outputs.
- [ ] `rg -n "eligible|reason|repo_commit_sha|source_repo_url" manifests`
- [ ] `rg -n "schema_version|reason_code|generated_at_utc" manifests`
- [ ] No unresolved placeholder text remains in new script/docs.

## Risks / rollback notes

- GitHub/API variability may affect repo metadata resolution; include clear fallback/unknown states.
- Overly strict checks may reduce candidate count; this is acceptable for initial baseline.
- If output schema drifts, update extraction spec and `_INDEX.md` references in the same change.
