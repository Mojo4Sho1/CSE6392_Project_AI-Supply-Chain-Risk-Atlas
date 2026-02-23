# Next Task

**Last updated:** 2026-02-23  
**Owner:** Joe + Codex

## Task summary

Implement the first minimal ingestion/eligibility script from the existing contract spec, using `data/models.csv` as input and producing manifest/provenance outputs for each candidate model.

## Why this task is next

- Authoritative specs and routing index are now in place.
- Environment setup and candidate manifest schema are established.
- Pipeline progress now depends on moving from contract docs to a runnable ingestion baseline.

## Scope (in)

- Implement initial script (path to be chosen during implementation, e.g., `scripts/ingest_repo_artifacts.py`) that:
  - reads `data/models.csv`,
  - validates required fields,
  - evaluates strict eligibility checks,
  - writes per-model manifest index/outcome metadata under `manifests/<model_id>/`.
- Ensure outputs include key provenance fields:
  - source repo URL,
  - resolved reference/commit when available,
  - fetch/evaluation timestamp,
  - explicit eligibility status and reason code.
- Add brief usage documentation for running the script in the shared conda env.

## Scope (out)

- Full OSV scan integration.
- Graph construction and reporting.
- Automated Hugging Face ranking/selection policy.

## Dependencies / prerequisites

- Environment + workflow:
  - `environment.yml`
  - `AGENTS.md`
- Data and specs:
  - `data/models.csv`
  - `docs/specs/data-sourcing-and-eligibility.md`
  - `docs/specs/extraction-and-normalization.md`
- Routing:
  - `docs/specs/_INDEX.md`

## Implementation notes

- Keep implementation minimal and deterministic.
- Treat strict eligibility failures as expected outcomes, not hard crashes.
- Keep reason codes stable and machine-readable for downstream analysis.

## Subtasks

- [ ] Create ingestion script following contract semantics.
- [ ] Create/validate output schema for `manifests/<model_id>/manifest_index.json`.
- [ ] Add explicit eligibility reason taxonomy (e.g., unreachable repo, no supported artifacts, parse failure).
- [ ] Add short run instructions to `README.md` or script header docstring.

## Acceptance criteria (definition of done)

- Script runs from shared conda env and processes `data/models.csv` end-to-end.
- At least one successful and one failed eligibility path are represented in output metadata (using sample rows if needed).
- Output files are deterministic and reproducible for same inputs.
- Handoff docs are updated with outcomes and next OSV integration task.

## Verification checklist

- [ ] `python <script_path> --help` works.
- [ ] Running script against `data/models.csv` produces `manifests/<model_id>/manifest_index.json` outputs.
- [ ] `rg -n "eligible|reason|repo_commit_sha|source_repo_url" manifests`
- [ ] No unresolved placeholder text remains in new script/docs.

## Risks / rollback notes

- GitHub/API variability may affect repo metadata resolution; include clear fallback/unknown states.
- Overly strict checks may reduce candidate count; this is acceptable for initial baseline.
- If output schema drifts, update extraction spec and `_INDEX.md` references in the same change.
