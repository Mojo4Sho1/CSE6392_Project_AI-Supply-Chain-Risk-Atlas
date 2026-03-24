# Next Task

**Last updated:** 2026-03-24
**Owner:** Joe

## Task summary

Implement M2 OSV scan and normalization: build `scripts/run_osv_scan.py` that reads eligible manifests from `manifests/` and produces `osv/<model_id>/raw.json` and `osv/<model_id>/normalized.json` outputs, then wire it into `make scan`.

**Task queue references:** T-015 through T-016 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Phase 1 (M1 ingestion) is complete. All 13 CSV candidates have `manifests/<model_id>/manifest_index.json` outputs.
- T-014 is now complete: OSV-Scanner is installed via Homebrew and verified from within the conda environment.
- The next milestone gap is scanning those artifacts for known vulnerabilities and normalizing outputs for graph construction.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-015:** Implement `scripts/run_osv_scan.py` + tests
2. **T-016:** Add `make scan` target to Makefile
3. Run end-to-end smoke verification on the current `manifests/` corpus

## Scope (in)

- Implement `scripts/run_osv_scan.py` that:
  - reads `manifests/<model_id>/manifest_index.json` for each eligible model,
  - fetches or locates the dependency artifact (use `dependency_artifact_url` from manifest or re-fetch),
  - runs OSV-Scanner on the artifact file(s),
  - writes raw OSV output to `osv/<model_id>/raw.json`,
  - normalizes to `osv/<model_id>/normalized.json` per schema in `docs/specs/artifact-schemas.md`.
- Enforce canonical `eligibility_reason_code` and `vuln_status` values.
- Write unit tests and smoke tests (see `AGENTS.md` testing policy).
- Add `make scan` target to `Makefile`.

## Scope (out)

- Graph construction and reporting (Phases 3–4).
- Re-running M1 ingestion (use existing manifests as input).
- Automated model selection or CSV updates.

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs: `manifests/<model_id>/manifest_index.json` (produced by M1)
- Specs (read only what's needed):
  - `docs/specs/extraction-and-normalization.md` — OSV scan contract, normalized schema
  - `docs/specs/artifact-schemas.md` — `osv/<model_id>/normalized.json` schema, enums
  - `docs/specs/pipeline-execution-contract.md` — CLI flags, exit codes, retry policy
  - `docs/specs/testing-and-validation.md` — test coverage requirements, M2 gate

## Implementation notes

- OSV-Scanner is already installed and verified via `brew install osv-scanner`; treat it as an external prerequisite on `PATH`, not part of `environment.yml`.
- The scan script should re-fetch artifact content (or cache it from manifests phase) and write to a temp file before scanning, since OSV-Scanner operates on local files.
- For unpinned dependencies: set `vuln_status=unknown` per DEC-003.
- Record scanner name and version in `normalized.json` provenance fields.
- Ineligible models (from M1) must be skipped with a log entry, not cause an error.
- Run `pytest` / `make test` after every code change.
- Exit codes: 0=success, 2=input error (bad manifest), 3=OSV-Scanner missing, 4=fatal error.

## Acceptance criteria (definition of done)

- `python scripts/run_osv_scan.py --help` works; CLI flags match contract.
- `make scan` runs the scan script.
- Each eligible model has paired `osv/<model_id>/raw.json` + `osv/<model_id>/normalized.json`.
- Normalized files validate against the schema in `docs/specs/artifact-schemas.md`.
- Scanner name and version recorded in all normalized outputs.
- All tests pass (`make test`).
- Handoff docs updated with outcomes; `NEXT_TASK.md` points to Phase 3.

## Verification checklist

- [x] `osv-scanner --version` works in conda env
- [ ] `python scripts/run_osv_scan.py --help` works
- [ ] `make scan` completes without error
- [ ] `osv/<model_id>/raw.json` produced for each eligible model
- [ ] `osv/<model_id>/normalized.json` produced for each eligible model, validates against schema
- [ ] `schema_version`, `generated_at_utc`, `scanner.name`, `scanner.version` present in all normalized files
- [ ] Ineligible models skipped (not scanned, not crashing)
- [ ] `make test` passes (91+ tests)
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-015 through T-016 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 2
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed milestone checklist state, acceptance gates, or cross-phase verification readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on Phase 3 (M3 graph construction), following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- OSV-Scanner is installed outside conda, so failures may come from shell `PATH` differences between interactive terminals and scripted runs.
- GitHub rate limiting during artifact re-fetching: reuse fetched content from M1 phase if possible, or implement caching.
- If OSV-Scanner output format changes, normalization logic must be updated; keep the schema version check prominent.
