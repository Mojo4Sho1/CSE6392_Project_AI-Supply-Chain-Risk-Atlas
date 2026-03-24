# Current Status

**Last updated:** 2026-03-24
**Owner:** Joe

## Current focus

Phase 2 is complete. The project is ready to start Phase 3 graph construction from the normalized OSV outputs in `osv/`.

## Completed in current focus

- Implemented all Phase 2 tasks (T-015 through T-016):
  - `scripts/run_osv_scan.py` — M2 CLI pipeline that loads eligible manifests, re-fetches artifacts, runs `osv-scanner`, writes `osv/<model_id>/raw.json`, and normalizes to `osv/<model_id>/normalized.json`
  - `scripts/_utils/osv_scan.py` — direct-dependency parsing, scanner version parsing, vulnerability/status normalization, severity bucketing, and deterministic package merging
  - `Makefile` — added `make scan`
  - `tests/unit/test_osv_scan.py` — unit coverage for requirements/pyproject/package.json parsing, scanner version parsing, and normalized output rules
  - `tests/integration/test_run_osv_scan.py` — integration coverage for eligible/ineligible/dry-run/bad-manifest/missing-scanner paths, synthetic `pyproject.toml` handling, and empty-package outputs
- Generated live Phase 2 outputs for the current corpus:
  - `osv/*/raw.json` and `osv/*/normalized.json` produced for all 13 manifest directories
  - scanner provenance recorded as `osv-scanner` version `2.3.5` in every normalized file
  - 322 normalized package records emitted across the 13 models
  - 21 normalized package records currently have `vuln_status="vulnerable"`
- Handled two real-data M2 edge cases:
  - `pyproject.toml` artifacts are converted to temporary synthetic `requirements.txt` inputs because `osv-scanner 2.3.5` does not directly scan `pyproject.toml`
  - `stabilityai/stable-diffusion-xl-base-1.0` produces an empty normalized package list because the recorded `pyproject.toml` declares no scanable package dependencies

## Passing checks

- `make test`: **105 tests passed, 0 failures**
- `python scripts/run_osv_scan.py --help`: exits 0, all common CLI flags shown
- `make scan`: completed successfully against the live `manifests/` corpus
- Output contract verification:
  - **13 raw outputs** and **13 normalized outputs**
  - every normalized file has `schema_version="1.0"`, `generated_at_utc` with `Z` suffix, and `scanner.name` / `scanner.version`
  - normalized files are present for every eligible manifest

## Known gaps/blockers

- Phase 3 remains open: `scripts/build_risk_graph.py`, graph tests, and `make graph`
- Live M2 execution still depends on external network access plus `osv-scanner` being available on `PATH`
- One model (`stabilityai/stable-diffusion-xl-base-1.0`) has zero normalized packages; the graph builder should still emit the model node with zero `uses_package` edges

## Active coordination notes

- T-015 and T-016 are complete and verified locally
- `osv/` is now the authoritative input boundary for Phase 3
- The next agent should start with T-017 (`build_risk_graph.py`) and then T-018 (`make graph`)

## Next task (single target)

Implement Phase 3 M3 graph construction from `osv/<model_id>/normalized.json`. See `NEXT_TASK.md` for details and `TASK_QUEUE.md` for the full backlog.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
