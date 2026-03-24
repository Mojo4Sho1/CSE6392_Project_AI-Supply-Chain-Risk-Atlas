# Current Status

**Last updated:** 2026-03-24
**Owner:** Joe

## Current focus

Phase 2 setup is partially complete. M1 is complete and the project is ready to implement M2 OSV scanning.

## Completed in current focus

- Implemented all Phase 1 tasks (T-007 through T-013):
  - `scripts/_utils/model_id.py` — 7-step deterministic `model_id` normalization with SHA-1 hash suffix; sentinel-based algorithm preserves `--` separator through hyphen-collapse step
  - `scripts/_utils/csv_parser.py` — strict v1 schema validation; shorthand likes parsing (`2.59k` → 2590); legacy column rejection (exit 2); all required/optional columns handled
  - `scripts/_utils/artifact_discovery.py` — GitHub raw content fetching with hint URL strategy; fallback probing for 9 recognized artifacts; retry with backoff; blob→raw URL conversion; parse-validity checks (TOML, JSON, UTF-8)
  - `scripts/_utils/eligibility.py` — all 10 canonical `eligibility_reason_code` values mapped; error_code-first evaluation order
  - `scripts/_utils/json_utils.py` — atomic writes, stable key ordering, UTC timestamps, trailing newline
  - `scripts/ingest_repo_artifacts.py` — full CLI contract (`--input`, `--output-root`, `--snapshot-timestamp`, `--dry-run`, `--log-level`); exit codes 0/2/4; per-candidate logging
  - `Makefile` — `make test` and `make ingest` targets
  - `tests/unit/` — 82 unit tests across model_id, csv_parser, artifact_discovery, eligibility
  - `tests/integration/test_ingest.py` — 9 integration tests covering eligible/ineligible/dry-run/determinism/no-artifacts paths
  - `tests/fixtures/` — 5 fixture CSVs for all required negative paths
  - conda env created: `ai-supply-chain-risk-atlas` (Python 3.11)
- Verified T-014 prerequisite:
  - OSV-Scanner installed successfully via Homebrew on macOS
  - `osv-scanner --version` works from within the activated `ai-supply-chain-risk-atlas` conda environment
  - repo setup guidance should treat OSV-Scanner as an external prerequisite on `PATH`, not a package managed by `environment.yml`

## Passing checks

- `make test` (pytest -q): **91 tests passed, 0 failures**
- `python scripts/ingest_repo_artifacts.py --help`: exits 0, all flags shown
- Legacy header fixture: exits 2 with descriptive error message
- End-to-end ingest on `data/models.csv`: **13/13 eligible**, all manifests written to `manifests/`
- All 13 manifest files validated: correct `schema_version`, `generated_at_utc` with Z suffix, trailing newline, stable key ordering
- `conda env create -f environment.yml`: environment created successfully
- `osv-scanner --version`: works inside the activated conda env after Homebrew install

## Known gaps/blockers

- All 13 models are eligible in real data (no real ineligible case). Ineligible path is covered by mocked integration tests.
- Makefile hardcodes conda env Python path — next agent may want to use `conda run` or `$(CONDA_PREFIX)/bin/python` for portability.
- M2 implementation work remains open: `scripts/run_osv_scan.py`, normalization logic, tests, and `make scan`.

## Active coordination notes

- T-014 is complete and verified locally.
- Next agent should start with T-015 (implement `run_osv_scan.py`) and T-016 (`make scan`).
- M1 output (`manifests/<model_id>/manifest_index.json`) is now available as Phase 2 input.

## Next task (single target)

Implement Phase 2 M2 scanning and normalization. See `NEXT_TASK.md` for details and `TASK_QUEUE.md` for the full backlog.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
