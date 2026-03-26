# Current Status

**Last updated:** 2026-03-26
**Owner:** Joe

## Current focus

The optional local dashboard showcase is implemented and verified, and the next major product-facing question is still whether the current Plotly renderer is good enough to keep. In parallel, the repo now also contains a simple LaTeX report scaffold so the final write-up can be drafted in-repo before moving to Overleaf.

## Completed in current focus

- Completed T-024 through T-025 and T-028:
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
- The only open question is optional: whether the current Plotly renderer is visually strong enough, or whether a Cytoscape follow-on would materially improve the demo
- `make dashboard` needs a real local socket bind; in the sandbox it reaches startup and then requires elevated launch permissions to complete the bind
- The report scaffold is ready for editing, but local PDF compilation was not verified because no TeX toolchain is installed in this environment

## Active coordination notes

- The dashboard now uses an explicit data/view/render split so a future `dash-cytoscape` renderer can be added without rewriting artifact loading or filter/detail logic
- `docs/specs/dashboard-showcase.md` is aligned with the implemented Plotly dashboard and the future renderer seam
- `paper/final_report.tex` is intentionally a simple single-file LaTeX draft, modeled after the user's preferred style, so it can be copied into Overleaf later with minimal restructuring
- No `PROJECT_CHECKLIST.md` milestone or gate state changed in this batch; this was a documentation/report-scaffold addition rather than a new pipeline milestone
- The next agent should start with T-026: review the live Plotly dashboard and make an explicit keep-vs-Cytoscape recommendation before opening a renderer migration batch

## Next task (single target)

Evaluate the live dashboard UX and decide whether the project should keep the current Plotly renderer or open an optional Cytoscape follow-on. See `NEXT_TASK.md` for the current brief and `TASK_QUEUE.md` for the backlog.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
