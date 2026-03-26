# Current Status

**Last updated:** 2026-03-26
**Owner:** Joe

## Current focus

Dashboard Redesign Stage 0 is complete. The next engineering batch is now **Dashboard Redesign Stage 1: new app shell, layout, and theme**, using the new layout/theme/controller seams added in this batch.

## Completed in current focus

- Completed T-029:
  - added dedicated dashboard theme and branding-path support in `scripts/_utils/dashboard_theme.py`
  - added a renderer-agnostic controller in `scripts/_utils/dashboard_controller.py`
  - split the Dash component tree into `scripts/_utils/dashboard_layout.py` so future shell work does not require callback rewiring
  - reduced `scripts/_utils/dashboard_app.py` to a thin app factory/callback layer and wired Dash explicitly to the repo `assets/` directory
  - updated `scripts/_utils/dashboard_render_plotly.py` and `assets/dashboard.css` to consume centralized theme tokens while preserving the current visual behavior
  - scaffolded `assets/branding/README.md` with the default logo location `assets/branding/ai_supply_chain_risk_atlas_logo.png`
  - documented the post-Stage-0 dashboard file responsibilities in `docs/dashboard_architecture_note.md`
  - added Stage 0 regression coverage:
    - `tests/unit/test_dashboard_theme.py`
    - `tests/unit/test_dashboard_controller.py`
    - updated `tests/integration/test_run_dashboard.py`
  - updated `docs/handoff/QUICK_REFERENCE.md` so fresh agents can route directly to the new dashboard files
- Live artifact baseline remains unchanged:
  - `graphs/global.graphml` still contains **289 nodes** and **322** `uses_package` edges
  - the dashboard corpus remains **13 models** and **276 packages**
  - the live summary still reports **21** reused vulnerable packages

## Passing checks

- `python scripts/run_dashboard.py --help`: **exits 0** when run with the repo’s configured conda interpreter
- Dashboard-focused regression suite:
  - `python -m pytest -q tests/unit/test_dashboard_theme.py tests/unit/test_dashboard_controller.py tests/unit/test_dashboard_data.py tests/unit/test_dashboard_view.py tests/unit/test_dashboard_render_plotly.py tests/integration/test_run_dashboard.py`
  - **17 passed**
- `make test`: **131 passed, 0 failures**
- Dashboard runtime verification:
  - `make dashboard` reached the Dash startup banner against the live repo artifacts, then exited because local port `127.0.0.1:8050` was already occupied by another Python process on this workstation snapshot
  - `python scripts/run_dashboard.py --graph graphs/global.graphml --summary reports/summary.json --table reports/summary.csv --host 127.0.0.1 --port 8060` launched successfully with elevated local bind permissions and was then manually interrupted

## Known gaps/blockers

- Stage 1 through Stage 6 remain to be implemented one batch at a time
- The dashboard still uses the pre-redesign stacked prototype shell; this batch prepared structure but did not deliver the new graph-first layout
- Port `8050` was already in use during this batch, so default-port launch verification could not be left running even though the app itself started successfully
- The report scaffold is still not locally compiled because no TeX toolchain is installed in this environment

## Active coordination notes

- Dashboard responsibilities are now intentionally split:
  - `dashboard_data.py` for artifact loading and canonical state
  - `dashboard_view.py` for pure filter/search/detail logic
  - `dashboard_controller.py` for interaction-state orchestration
  - `dashboard_layout.py` for Dash component structure
  - `dashboard_render_plotly.py` for the current renderer
  - `dashboard_theme.py` for theme tokens and branding asset paths
- `assets/branding/` is now the reserved home for optional logo files; Stage 2 can experiment with placement without inventing a new path
- Stage 1 should focus primarily on `scripts/_utils/dashboard_layout.py`, `scripts/_utils/dashboard_theme.py`, and `assets/dashboard.css`
- Plotly remains the renderer through Stages 0-2; Cytoscape is still deferred to Stage 3
- No core pipeline milestone gate changed in this batch; the progress was on the optional dashboard redesign track
- No spec changed in this batch, so `docs/specs/_INDEX.md` did not need an update

## Next task (single target)

Implement Dashboard Redesign Stage 1: new app shell, layout, and theme. See `NEXT_TASK.md` for the Stage 1 brief and `docs/dashboard_architecture_note.md` for the new file-responsibility map.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
