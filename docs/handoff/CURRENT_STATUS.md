# Current Status

**Last updated:** 2026-03-26
**Owner:** Joe

## Current focus

Dashboard Redesign Stage 1 is complete. The next engineering batch is now **Dashboard Redesign Stage 2: branding pass and visual refinement**, using the graph-first shell delivered in this batch.

## Completed in current focus

- Completed T-030:
  - rebuilt the dashboard shell in `scripts/_utils/dashboard_layout.py` around a top bar, left search/filter rail, center graph pane, and right selection inspector
  - converted atlas metrics into compact sidebar cards and moved reused-vulnerable package context into the left rail so the graph stays dominant above the fold
  - updated `scripts/_utils/dashboard_theme.py` and `assets/dashboard.css` to a dark-shell / light-canvas palette aligned with `docs/dashboard_redesign_plan.md`
  - updated `scripts/_utils/dashboard_render_plotly.py` so model labels, legend text, and empty-graph annotations use light-canvas text tokens instead of shell text tokens
  - added Stage 1 layout regression coverage in `tests/unit/test_dashboard_layout.py`
  - extended existing dashboard tests:
    - `tests/unit/test_dashboard_theme.py`
    - `tests/unit/test_dashboard_render_plotly.py`
    - `tests/integration/test_run_dashboard.py`
  - updated `docs/specs/dashboard-showcase.md` and `docs/specs/_INDEX.md` so the dashboard contract now describes the graph-first shell instead of the older overview-row layout
- Live artifact baseline remains unchanged:
  - `graphs/global.graphml` still contains **289 nodes** and **322** `uses_package` edges
  - the dashboard corpus remains **13 models** and **276 packages**
  - the live summary still reports **21** reused vulnerable packages

## Passing checks

- `python scripts/run_dashboard.py --help`: **exits 0** when run with the repo’s configured conda interpreter
- Dashboard-focused regression slice:
  - `/Applications/MiniConda/miniconda3/envs/ai-supply-chain-risk-atlas/bin/python -m pytest -q tests/unit/test_dashboard_layout.py tests/unit/test_dashboard_theme.py tests/unit/test_dashboard_render_plotly.py tests/integration/test_run_dashboard.py`
  - **9 passed**
- `make test`: **133 passed, 0 failures**
- Dashboard runtime verification:
  - `make dashboard` reached the Dash startup banner against the live repo artifacts, then exited because local port `127.0.0.1:8050` was already occupied by another program on this workstation snapshot
  - `/Applications/MiniConda/miniconda3/envs/ai-supply-chain-risk-atlas/bin/python scripts/run_dashboard.py --graph graphs/global.graphml --summary reports/summary.json --table reports/summary.csv --host 127.0.0.1 --port 8060` launched successfully against the live artifacts and was then manually interrupted

## Known gaps/blockers

- Stage 2 through Stage 6 remain to be implemented one batch at a time
- Stage 1 delivered the shell, but Stage 2 still needs branding/logo treatment, legend polish, badge refinement, and better empty-state finish work
- Port `8050` was already in use during this batch, so the documented default launch command could not be left running even though startup was confirmed
- The report scaffold is still not locally compiled because no TeX toolchain is installed in this environment

## Active coordination notes

- The Stage 1 shell is now the baseline:
  - top bar
  - left sidebar
  - center graph pane
  - right inspector
- Stage 2 should focus primarily on `scripts/_utils/dashboard_layout.py`, `scripts/_utils/dashboard_theme.py`, and `assets/dashboard.css`, with only small Plotly tweaks if the light-canvas presentation needs them
- `assets/branding/` remains the reserved home for optional logo files; Stage 2 should keep branding placement easy to enable, disable, or relocate without requiring an asset to exist
- Plotly remains the renderer through Stages 0-2; Cytoscape is still deferred to Stage 3
- Inspector behavior is still single-node only; compare mode remains out of scope
- Dashboard semantics and the M1-M4 artifact contract were intentionally left unchanged in this batch
- This batch updated the dashboard showcase spec routing to match the delivered Stage 1 shell

## Next task (single target)

Implement Dashboard Redesign Stage 2: branding pass and visual refinement. See `NEXT_TASK.md` for the Stage 2 brief and `docs/dashboard_redesign_plan.md` for the redesign acceptance criteria.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
