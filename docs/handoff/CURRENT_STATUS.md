# Current Status

**Last updated:** 2026-03-26
**Owner:** Joe

## Current focus

The optional local dashboard showcase is implemented and verified, and the redesign direction is now locked in `docs/dashboard_redesign_plan.md`. The next engineering batch is no longer a vague Plotly-vs-Cytoscape evaluation; it is **Dashboard Redesign Stage 0: audit and refactor preparation**, with Plotly retained for now and Cytoscape deferred to a later stage.

## Completed in current focus

- Completed T-024, T-025, T-026, and T-028:
  - added dashboard runtime dependencies to `environment.yml`: `dash` and `plotly`
  - implemented the swap-friendly dashboard stack:
    - `scripts/run_dashboard.py`
    - `scripts/_utils/dashboard_data.py`
    - `scripts/_utils/dashboard_view.py`
    - `scripts/_utils/dashboard_render_plotly.py`
    - `scripts/_utils/dashboard_app.py`
    - `assets/dashboard.css`
  - added dashboard tests:
    - `tests/dashboard_fixtures.py`
    - `tests/unit/test_dashboard_data.py`
    - `tests/unit/test_dashboard_view.py`
    - `tests/unit/test_dashboard_render_plotly.py`
    - `tests/integration/test_run_dashboard.py`
  - added `make dashboard` and extended `make validate` to include `python scripts/run_dashboard.py --help`
  - updated `README.md` and `docs/specs/dashboard-showcase.md` to document the single-page Plotly dashboard, launch flow, and future renderer seam
  - reviewed the live dashboard and replaced the old binary renderer decision path with a staged redesign roadmap in `docs/dashboard_redesign_plan.md`
  - locked the redesign direction:
    - graph-first application shell
    - dark shell with light graph canvas
    - single-node inspector workflow
    - package labels hidden by default
    - Plotly kept through Stages 0-2
    - Cytoscape migration deferred to Stage 3
    - implement one stage per batch only
  - added a simple repo-local final report scaffold:
    - `paper/final_report.tex`
    - `paper/README.md`
  - updated the repo layout notes in `README.md` so the new `paper/` directory is discoverable
- Live dashboard/runtime baseline:
  - dashboard startup reads the current live artifacts: `graphs/global.graphml`, `reports/summary.json`, `reports/summary.csv`
  - the live graph contains **289 nodes** and **322** `uses_package` edges
  - the explorer surfaces the current corpus of **13 models** and **276 packages**
  - the live summary still reports **21** reused vulnerable packages

## Passing checks

- `python scripts/run_dashboard.py --help`: **exits 0**
- `make test`: **128 passed, 0 failures**
- `make validate`: **passes**
- `make dashboard`: **launches successfully** on `http://127.0.0.1:8050` with the documented defaults when run outside the sandbox socket restriction; launch was manually interrupted after startup verification
- Existing core checks remain healthy:
  - `make all` passes from repo root
  - `graphs/global.graphml`, `reports/summary.json`, and `reports/summary.csv` all exist
  - both required PNG figures still exist under `figures/`
  - no unresolved decision markers remain in active README/spec/handoff docs
- Report-scaffold checks:
  - `paper/final_report.tex` exists and is prefilled with project-specific content
  - `paper/README.md` documents both repo-local editing and later Overleaf transfer
  - `latexmk` and `pdflatex` are not installed in the current environment, so the LaTeX draft was not compiled locally

## Known gaps/blockers

- No core project blockers remain
- The redesign itself is not implemented yet; only the roadmap is locked
- Stage 0 through Stage 6 remain to be completed one batch at a time
- `make dashboard` needs a real local socket bind; in the sandbox it reaches startup and then requires elevated launch permissions to complete the bind
- The report scaffold is ready for editing, but local PDF compilation was not verified because no TeX toolchain is installed in this environment

## Active coordination notes

- The dashboard now uses an explicit data/view/render split so a future `dash-cytoscape` renderer can be added without rewriting artifact loading or filter/detail logic
- `docs/specs/dashboard-showcase.md` is aligned with the implemented Plotly dashboard and the future renderer seam
- `docs/dashboard_redesign_plan.md` is now the authoritative roadmap for all dashboard redesign work
- Fresh agents should treat the redesign as a staged delivery:
  - Stage 0: audit and refactor preparation
  - Stage 1: new app shell, layout, and theme
  - Stage 2: branding and visual refinement
  - Stage 3: Cytoscape migration
  - Stage 4: inspector redesign
  - Stage 5: filters, search, and linked summaries
  - Stage 6: final polish
- `paper/final_report.tex` is intentionally a simple single-file LaTeX draft, modeled after the user's preferred style, so it can be copied into Overleaf later with minimal restructuring
- No `PROJECT_CHECKLIST.md` milestone or gate state changed in this batch; this was a documentation/report-scaffold addition rather than a new pipeline milestone
- The next agent should start with **T-029 / Stage 0 only** and avoid drifting into Stage 1 visual redesign in the same batch

## Next task (single target)

Implement Dashboard Redesign Stage 0: audit and refactor preparation. See `NEXT_TASK.md` for the stage brief and `TASK_QUEUE.md` for the staged backlog.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
