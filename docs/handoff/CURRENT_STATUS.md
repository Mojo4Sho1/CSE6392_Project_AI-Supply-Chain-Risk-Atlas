# Current Status

**Last updated:** 2026-03-24
**Owner:** Joe

## Current focus

Phase 3 is complete. The project is ready to start Phase 4 reporting from `graphs/global.graphml`.

## Completed in current focus

- Implemented all Phase 3 tasks (T-017 through T-018):
  - `scripts/build_risk_graph.py` — M3 CLI pipeline that loads `osv/<model_id>/normalized.json`, builds the global typed graph, validates required node/edge attributes, and writes `graphs/global.graphml`
  - `scripts/_utils/graph_build.py` — normalized-input loading, package-node deduplication, deterministic `uses_package` depth mapping, graph integrity checks, GraphML-safe `vuln_ids_json` encoding, and conservative package-annotation merging for duplicate package keys across models
  - `tests/unit/test_graph_build.py` — unit coverage for package deduplication, conservative vulnerability-annotation merge behavior, and depth validation
  - `tests/integration/test_build_risk_graph.py` — integration coverage for CLI help, GraphML output generation, package deduplication, and zero-package model preservation
  - `Makefile` — added `make graph`
- Generated live Phase 3 output for the current corpus:
  - `graphs/global.graphml` produced from all 13 normalized OSV outputs
  - graph contains **13 Model nodes**, **276 Package nodes**, and **322 `uses_package` edges**
  - zero-package model `stabilityai--stable-diffusion-xl-base-1.0--5eb3438c` is present with out-degree 0
- Clarified graph contract documentation:
  - `docs/specs/graph-semantics-and-metrics.md` now defines `node_type` / `edge_type`, the v1 depth rule (`direct=0`, `transitive=1`, `unknown=-1`), GraphML-safe `vuln_ids_json`, and deterministic duplicate-package merge behavior
  - `docs/specs/_INDEX.md` updated to reflect the expanded graph serialization/merge rules

## Passing checks

- `python scripts/build_risk_graph.py --help`: **exits 0**
- `make graph`: **completed successfully** and wrote `graphs/global.graphml`
- `make test`: **110 tests passed, 0 failures**
- Output contract verification:
  - **13 normalized inputs** consumed
  - graph counts match normalized inputs exactly: **13 models**, **276 unique packages**, **322 uses-package edges**
  - zero-package model preserved with **0 outgoing edges**

## Known gaps/blockers

- Phase 4 remains open: `scripts/generate_atlas_reports.py`, report tests, `make report`, and `make all`
- No report artifacts exist yet under `reports/` or `figures/`
- Reporting must parse package-node `vuln_ids_json` because GraphML stores scalar attributes only
- Dashboard work is now queued as a post-M4 local showcase track; no dashboard code exists yet

## Active coordination notes

- T-017 and T-018 are complete and verified locally
- `graphs/global.graphml` is now the authoritative input boundary for Phase 4
- The next agent should start with T-019 (`generate_atlas_reports.py`) and then T-020 (`make report` / `make all`)
- The Phase 4 brief now explicitly calls out `summary.csv` columns, report ordering rules, minimum figure outputs, and the current graph-size sanity baseline to reduce implementation ambiguity
- Added a new queued dashboard showcase track (`T-023` through `T-025`) using Dash + Plotly, but it remains explicitly deferred until after M4
- `PROJECT_CHECKLIST.md` milestone state did not change in this batch; the dashboard is tracked as a Phase 5 showcase extension rather than a new M1-M4 gate

## Next task (single target)

Implement Phase 4 M4 reporting from `graphs/global.graphml`. See `NEXT_TASK.md` for details and `TASK_QUEUE.md` for the full backlog.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
