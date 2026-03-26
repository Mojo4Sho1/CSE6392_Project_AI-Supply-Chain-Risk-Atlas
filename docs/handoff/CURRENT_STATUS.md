# Current Status

**Last updated:** 2026-03-26
**Owner:** Joe

## Current focus

Dashboard Redesign Stage 2 is now in progress. The current shell keeps the graph-first structure from Stage 1, but the active refinement direction is now **no visible logo in the UI** plus better supporting-panel placement beneath the graph.

## Completed in current focus

- Completed follow-up shell refinements within active T-031:
  - removed the bundled `assets/branding/ai_supply_chain_risk_atlas_logo.png` asset from the repo so the default dashboard presentation is clearly no-logo
  - updated `scripts/_utils/dashboard_layout.py` so the left rail stays focused on search and filters while `Snapshot Metrics` and `Reuse Hotspots` now live beneath the graph in the main pane
  - removed user-facing `model_id` references from the search copy, model inspector rows, and model hover content so the dashboard presents Hugging Face model names only
  - updated `assets/dashboard.css` to support the new bottom-of-dashboard insights row without changing dashboard semantics
  - extended dashboard layout tests so the metrics and hotspots panels are asserted under the main pane rather than the left sidebar
  - updated `assets/branding/README.md`, `docs/specs/dashboard-showcase.md`, and `docs/specs/_INDEX.md` to match the no-logo direction and lower insight-row layout
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
  - `make dashboard` launched successfully against the live repo artifacts on `127.0.0.1:8050` and was then manually interrupted after the Dash startup banner confirmed the shell booted cleanly

## Known gaps/blockers

- Stage 2 through Stage 6 remain to be implemented one batch at a time
- Stage 2 still needs legend polish, badge refinement, and better empty-state finish work
- The report scaffold is still not locally compiled because no TeX toolchain is installed in this environment

## Active coordination notes

- The Stage 1 shell remains the baseline:
  - top bar
  - left sidebar
  - center graph pane
  - right inspector
- Supporting context panels now belong beneath the graph, not in the left sidebar
- The current design direction is to omit a visible logo from the dashboard UI; rely on color/typography/layout branding instead
- The dashboard should present Hugging Face model names as the only user-facing model identifier; internal `model_id` values remain implementation details
- Stage 2 should focus primarily on `scripts/_utils/dashboard_layout.py`, `scripts/_utils/dashboard_theme.py`, and `assets/dashboard.css`, with only small Plotly tweaks if the light-canvas presentation needs them
- `assets/branding/` remains a reserved optional asset path, but the current default experience should not assume an asset is present
- Plotly remains the renderer through Stages 0-2; Cytoscape is still deferred to Stage 3
- Inspector behavior is still single-node only; compare mode remains out of scope
- Dashboard semantics and the M1-M4 artifact contract remain unchanged
- No `PROJECT_CHECKLIST.md` milestone or gate state changed in this follow-up batch

## Next task (single target)

Finish Dashboard Redesign Stage 2: branding pass and visual refinement. See `NEXT_TASK.md` for the remaining Stage 2 brief and `docs/dashboard_redesign_plan.md` for the redesign acceptance criteria.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
