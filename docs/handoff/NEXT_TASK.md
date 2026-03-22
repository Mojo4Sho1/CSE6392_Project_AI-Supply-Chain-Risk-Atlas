# Next Task

**Last updated:** 2026-03-21
**Owner:** Joe

## Task summary

Implement M1 ingestion and eligibility baseline: build `scripts/ingest_repo_artifacts.py` that reads `data/models.csv` and produces deterministic `manifests/<model_id>/manifest_index.json` outputs.

**Task queue references:** T-007 through T-013 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Phase 0 scaffolding is complete (CSV reconciled, specs aligned, agent docs created).
- All policy defaults are resolved in `docs/specs/decision-log.md` (DEC-001 through DEC-008).
- The highest-priority gap is turning M1 specs into runnable code.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

Tasks T-007 and T-008 have no interdependencies and can be started in parallel:

1. **T-007:** Implement `model_id` normalization utility + tests
2. **T-008:** Implement CSV parser with v1 schema validation + tests
3. **T-009:** Implement artifact discovery with hint support + tests
4. **T-010:** Implement eligibility evaluation + tests
5. **T-011:** Assemble `ingest_repo_artifacts.py` with CLI contract
6. **T-012:** Create Makefile with `ingest`/`test` targets
7. **T-013:** End-to-end M1 smoke test

## Scope (in)

- Implement `scripts/ingest_repo_artifacts.py` that:
  - reads `data/models.csv` (9-column v1 schema),
  - validates required fields and timestamp format,
  - parses human-readable shorthand for `hf_likes_at_snapshot` (e.g., "2.59k" → 2590),
  - uses `dependency_artifact_url` as hint when present,
  - evaluates strict eligibility checks,
  - writes per-model manifest under `manifests/<model_id>/`.
- Enforce canonical `eligibility_reason_code` values from `docs/specs/artifact-schemas.md`.
- Implement deterministic `model_id` normalization from `docs/specs/artifact-schemas.md`.
- Write unit tests and smoke tests (see `AGENTS.md` testing policy).
- Create `Makefile` with at least `make test` and `make ingest` targets.

## Scope (out)

- OSV scan integration (Phase 2).
- Graph construction and reporting (Phases 3–4).
- Automated Hugging Face ranking/selection policy.

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Data: `data/models.csv`
- Specs (read only what's needed per task):
  - `docs/specs/artifact-schemas.md` — schemas, enums, model_id normalization
  - `docs/specs/data-sourcing-and-eligibility.md` — CSV schema, eligibility rules
  - `docs/specs/extraction-and-normalization.md` — artifact fetching contract
  - `docs/specs/pipeline-execution-contract.md` — CLI flags, exit codes
  - `docs/specs/testing-and-validation.md` — test fixtures, coverage gates

## Implementation notes

- Keep implementation minimal and deterministic.
- Treat eligibility failures as expected outcomes, not crashes (exit code 0).
- `data/models.csv` is human-owned — read-only in code.
- Legacy CSV columns (`ranking_signal`, `selection_method`, `eligible`, `selection_source`) in header → reject with exit code 2.
- Run `pytest` after every code change (per `AGENTS.md` testing policy).
- Create Makefile/scripts for repeated commands (per `AGENTS.md` automation policy).

## Acceptance criteria (definition of done)

- Script runs from conda env and processes `data/models.csv` end-to-end.
- Invalid or legacy CSV header shapes fail with explicit input-contract error (exit 2).
- Manifest outputs conform to v1 schema and enum contracts.
- At least one eligible and one ineligible path represented in output or test fixtures.
- Output files are deterministic and reproducible for same inputs.
- All tests pass (`make test`).
- Handoff docs updated with outcomes; `NEXT_TASK.md` points to Phase 2.

## Verification checklist

- [ ] `python scripts/ingest_repo_artifacts.py --help` works
- [ ] `make test` passes
- [ ] `make ingest` produces `manifests/<model_id>/manifest_index.json` for each CSV row
- [ ] Legacy-header fixture fails with exit code 2
- [ ] Bad timestamp fixture fails validation
- [ ] Bad numeric fixture fails validation
- [ ] Manifest JSON files validate against schema (stable keys, trailing newline, Z-suffix timestamps)
- [ ] No unresolved placeholder text in new code/docs

## Risks / rollback notes

- GitHub API variability may affect repo metadata resolution; include fallback/unknown states.
- Overly strict checks may reduce eligible count; acceptable for initial baseline.
- If output schema drifts, update `artifact-schemas.md` and `_INDEX.md` in the same change.
