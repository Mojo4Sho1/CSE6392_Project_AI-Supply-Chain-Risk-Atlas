# Current Status

**Last updated:** 2026-03-24
**Owner:** Joe

## Current focus

Phase 5 validation and documentation are complete. The core M1-M4 pipeline is validated and documented; the only remaining queued work is the optional local dashboard showcase track.

## Completed in current focus

- Completed T-021 through T-023:
  - ran the full Phase 5 local validation pass against the implemented M1-M4 pipeline and recorded the outcomes in `docs/handoff/PROJECT_CHECKLIST.md`
  - added `make validate` to bundle the repeated validation workflow: CLI `--help` smoke checks, `make all`, `make test`, artifact existence checks, and the unresolved-decision grep
  - reconciled `README.md`, `docs/specs/artifact-schemas.md`, and `docs/specs/_INDEX.md` with the actual v1 pipeline by removing stale `data/models.json` references and documenting the manifest-based freeze boundary
  - refreshed dashboard routing docs so the next agent can go straight to `docs/specs/dashboard-showcase.md`
- Current live artifact baseline:
  - **13** manifest files under `manifests/<model_id>/manifest_index.json`
  - **13** paired OSV raw outputs and **13** normalized outputs
  - `graphs/global.graphml`
  - `reports/summary.json`
  - `reports/summary.csv`
  - `figures/reused_vulnerable_packages.png`
  - `figures/impacted_model_count_distribution.png`
- Current live report baseline from `graphs/global.graphml` / `reports/summary.json`:
  - **13 models** in `per_model_metrics`
  - **276 unique packages**
  - average packages per model: **24.76923076923077**
  - average direct packages per model: **10.692307692307692**
  - average transitive packages per model: **14.076923076923077**
  - **21** `reused_vulnerable_packages` entries in the current summary output

## Passing checks

- `python scripts/ingest_repo_artifacts.py --help`: **exits 0**
- `python scripts/run_osv_scan.py --help`: **exits 0**
- `python scripts/build_risk_graph.py --help`: **exits 0**
- `python scripts/generate_atlas_reports.py --help`: **exits 0**
- `make all`: **passes** from repo root (current run reused staged outputs; no failures)
- `make test`: **114 passed, 0 failures**
- `make validate`: **passes**
- Output contract spot checks:
  - `reports/summary.json` contains the required top-level fields: `schema_version`, `generated_at_utc`, `snapshot_timestamp_utc`, `graph_source`, `global_metrics`, `per_model_metrics`, `reused_vulnerable_packages`
  - `reports/summary.csv` contains **13** data rows plus header, with the required six columns in the correct order
  - both required PNG figures exist under `figures/`
  - no unresolved decision markers remain in active README/spec/handoff docs

## Known gaps/blockers

- The local Dash/Plotly showcase is not implemented yet; no `scripts/run_dashboard.py` entrypoint or `make dashboard` target exists
- `make all` still reuses staged outputs by design; use `make clean` before `make all` only when intentionally testing a full regeneration from scratch

## Active coordination notes

- `docs/handoff/PROJECT_CHECKLIST.md` now records the Phase 5 validation state and cross-phase verification outcomes for the current repository snapshot
- `docs/specs/dashboard-showcase.md` is the authoritative contract for the remaining showcase work
- The next agent should start with T-024 and T-025: implement the read-only dashboard against the existing graph/report artifacts, then add the launch target and README instructions

## Next task (single target)

Implement the optional local dashboard showcase track. See `NEXT_TASK.md` for the current brief and `TASK_QUEUE.md` for the remaining backlog.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
