# Current Status

**Last updated:** 2026-03-26
**Owner:** Joe

## Current focus

Dashboard Redesign Stage 2 is complete. The current dashboard now keeps the no-logo graph-first shell from Stage 1 while adding a compact in-shell legend, clearer Stage 2 surface polish, and clickable OSV advisory links in the package inspector.

## Completed in current focus

- Completed T-031, Dashboard Redesign Stage 2: branding pass and visual refinement
- Updated `scripts/_utils/dashboard_layout.py` so the graph pane now includes a compact custom legend, clearer supporting microcopy, refined badge treatment, and package-inspector vulnerability IDs that open `https://osv.dev/vulnerability/<ID>` in a new tab
- Applied a follow-up shell tweak so the dashboard no longer shows the extra top-bar or above-graph explainer copy, and the graph legend now sits inline to the left of the scope/selection chips rather than stacking above them
- Applied a second follow-up shell tweak so the graph panel header now uses two compact full-width rows: a horizontal status row and a compressed horizontal legend strip, allowing the graph canvas to start higher in the panel
- Applied a third follow-up shell tweak so the four app-state metadata chips now live in a compact header ribbon beneath the title, while the graph legend is docked directly onto the graph frame as a compact overlay instead of occupying standalone panel height
- Updated `scripts/_utils/dashboard_render_plotly.py` so the Plotly-native legend is disabled in favor of the new shell-level legend, while the light-canvas renderer semantics remain unchanged
- Updated `assets/dashboard.css` with Stage 2 polish for top-bar badge tones, legend styling, control microcopy, empty-state treatment, and interactive advisory-link chips
- Extended dashboard tests so the layout and integration suite assert the new legend contract and the unit suite verifies OSV advisory link generation
- Updated `docs/specs/dashboard-showcase.md` and `docs/specs/_INDEX.md` so the dashboard contract now explicitly requires external OSV advisory links in the package inspector
- Live artifact baseline remains unchanged:
  - `graphs/global.graphml` still contains **289 nodes** and **322** `uses_package` edges
  - the dashboard corpus remains **13 models** and **276 packages**
  - the live summary still reports **21** reused vulnerable packages

## Passing checks

- `python scripts/run_dashboard.py --help`: **exits 0** when run with the repo’s configured conda interpreter
- Dashboard-focused regression slice:
  - `/Applications/MiniConda/miniconda3/envs/ai-supply-chain-risk-atlas/bin/python -m pytest -q tests/unit/test_dashboard_layout.py tests/unit/test_dashboard_render_plotly.py tests/integration/test_run_dashboard.py`
  - **8 passed**
- `make test`: **134 passed, 0 failures**
- Dashboard runtime verification:
  - `make dashboard` reached the Dash startup banner on `127.0.0.1:8050` and then hit the expected local port-conflict failure because port `8050` was already occupied
  - `/Applications/MiniConda/miniconda3/envs/ai-supply-chain-risk-atlas/bin/python scripts/run_dashboard.py --graph graphs/global.graphml --summary reports/summary.json --table reports/summary.csv --host 127.0.0.1 --port 8060` launched successfully against the live artifacts and was then manually interrupted after the startup banner confirmed the app booted cleanly

## Known gaps/blockers

- Stage 3 through Stage 6 remain to be implemented one batch at a time
- Stage 3 still needs the renderer migration from Plotly to Cytoscape, including any required dependency/spec updates for that new renderer
- The report scaffold is still not locally compiled because no TeX toolchain is installed in this environment

## Active coordination notes

- Stage 2 is complete; the next dashboard batch should focus only on Stage 3 Cytoscape migration
- The dedicated Stage 3 work branch is `dashboard-stage3-cytoscape`; the next agent should work there instead of `main`
- Keep `main` as the currently approved Plotly fallback baseline until the Cytoscape result is reviewed and explicitly accepted
- Keep the graph-first shell intact:
  - top bar
  - left sidebar
  - center graph pane
  - right inspector
- Keep the lower insight row beneath the graph; do not move those panels back into the left sidebar
- Keep the no-logo default intact; rely on color, typography, spacing, and the new legend treatment instead
- Keep the slimmer top-of-graph presentation intact; do not reintroduce the removed explainer copy above the graph or beneath the title bar unless requirements change
- Keep the graph header as two compact horizontal rows rather than returning to tall legend cards or stacked status-card layouts
- Keep high-level app-state metadata in the header ribbon, not inside the graph panel, and keep the legend visually attached to the graph frame as a compact overlay
- Keep Hugging Face model names as the only user-facing model identifier; internal `model_id` values remain hidden implementation details
- Keep the new external OSV-link behavior in the package inspector; do not add local advisory-description storage unless the spec changes
- Keep Plotly out of new feature work unless it is needed as a migration fallback seam; Cytoscape is the next intended renderer
- Preserve single-node inspector behavior; compare mode remains out of scope
- `PROJECT_CHECKLIST.md` milestone gates remain unchanged, but the optional showcase-track redesign readiness has advanced to Stage 3

## Next task (single target)

Begin Dashboard Redesign Stage 3: Cytoscape migration on branch `dashboard-stage3-cytoscape`. See `NEXT_TASK.md` for the implementation brief and `docs/dashboard_redesign_plan.md` for the Stage 3 acceptance criteria.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
