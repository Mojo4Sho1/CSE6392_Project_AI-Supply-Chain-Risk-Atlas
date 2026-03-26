# Next Task

**Last updated:** 2026-03-26
**Owner:** Joe

## Task summary

Implement **Dashboard Redesign Stage 3: Cytoscape migration** from `docs/dashboard_redesign_plan.md`. Stage 2 is now complete, so the next batch should replace the active Plotly graph surface with Cytoscape while preserving the existing graph-first shell, current filtering/search semantics, and the renderer-agnostic data/view/controller seams.

**Task queue references:** T-032 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Stage 2 is complete: the dashboard now has the no-logo branding pass, compact in-shell legend, improved panel treatment, and clickable OSV advisory links in the package inspector.
- The redesign plan explicitly makes Cytoscape migration the next bounded stage before any Stage 4 selection-workflow redesign.
- The current dashboard-showcase contract and environment are still Plotly-oriented, so this is the right point to update the renderer contract deliberately instead of letting renderer drift happen implicitly.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-032:** Read `docs/dashboard_redesign_plan.md` Stage 3, `docs/handoff/CURRENT_STATUS.md`, `docs/specs/dashboard-showcase.md`, and `docs/dashboard_architecture_note.md`
2. **T-032:** Update `docs/specs/dashboard-showcase.md` first if the renderer/runtime contract needs to change for Cytoscape, and update `docs/specs/_INDEX.md` in the same batch
3. **T-032:** Add the Cytoscape renderer path and any required dependency/runtime wiring (likely including `environment.yml`, dashboard renderer modules, and app/layout integration)
4. **T-032:** Preserve the Stage 1 shell and Stage 2 polish while migrating only the graph surface and renderer-specific interactions
5. **T-032:** Extend tests, verify the live dashboard runtime, then update handoff docs so Stage 4 can focus on selection workflow rather than renderer migration

## Scope (in)

- Dashboard Stage 3 only, as defined in `docs/dashboard_redesign_plan.md`
- Renderer migration from Plotly to Cytoscape for the graph surface
- Any required dependency/config/doc updates needed to support Cytoscape locally
- Preservation of the current graph-first shell:
  - top bar
  - left sidebar
  - center graph pane
  - right inspector
  - lower insight row beneath the graph
- Preservation of current search, filter, and single-node selection semantics unless the new renderer requires a minimal presentation-layer adaptation
- Label strategy work required by Stage 3:
  - package labels hidden by default
  - model labels only if legibility remains acceptable
- Tests for the new renderer behavior and startup/runtime path
- Write unit tests and smoke tests for all new code (per `AGENTS.md` testing policy)

## Scope (out)

- Stage 4 inspector/selection-workflow redesign
- Compare mode or multi-node selection
- Stage 5 interactive summary-table/navigation work
- Changes to validated M1-M4 pipeline outputs or schemas
- Reintroducing a visible logo or restructuring the shell again

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `graphs/global.graphml`
  - `reports/summary.json`
  - `reports/summary.csv`
  - Current dashboard code:
    - `scripts/_utils/dashboard_data.py`
    - `scripts/_utils/dashboard_view.py`
    - `scripts/_utils/dashboard_controller.py`
    - `scripts/_utils/dashboard_layout.py`
    - `scripts/_utils/dashboard_render_plotly.py`
    - `scripts/_utils/dashboard_app.py`
    - `assets/dashboard.css`
- Specs (read only what's needed):
  - `docs/dashboard_redesign_plan.md` — authoritative Stage 3 renderer target
  - `docs/specs/dashboard-showcase.md` — current dashboard runtime/interaction contract; likely needs an explicit Stage 3 update first
  - `docs/handoff/CURRENT_STATUS.md` — exact Stage 2 completion state and live verification caveats
  - `docs/dashboard_architecture_note.md` — dashboard layer map and renderer seam expectations

## Implementation notes

- Update the spec first if Cytoscape behavior is not already covered; do not let the renderer change outpace the written contract.
- Keep `dashboard_data.py`, `dashboard_view.py`, and the core filtering logic renderer-agnostic.
- Prefer adding a dedicated Cytoscape renderer module rather than overloading the Plotly renderer file with divergent behavior.
- Keep the no-logo direction, lower insight row, Hugging Face-first naming, and external OSV advisory links intact.
- Preserve the current stripped-back top bar with the compact header metadata ribbon, and keep the graph legend attached directly to the graph frame as a small overlay rather than a standalone panel header.
- Keep package labels hidden by default and avoid graph-wide label clutter.
- Do not fold Stage 4 graph-focus or neighborhood-highlighting work into this batch unless it is strictly required for baseline Cytoscape selection parity.
- If port `8050` is occupied locally during manual verification, confirm the default command behavior first and then use a temporary alternate port without changing the documented default.
- Run `make test` after code changes and treat expected failure paths as normal outcomes, not crashes.

## Acceptance criteria (definition of done)

- Cytoscape replaces Plotly as the active graph renderer without breaking the dashboard runtime contract
- The graph remains visually dominant inside the existing dark-shell / light-canvas UI
- Existing graph semantics, filters, search behavior, and single-node selection still work
- Package labels are hidden by default and the label strategy avoids clutter
- The renderer seam remains clear enough that dashboard data/view-model logic is still reusable
- All tests pass (`make test`)
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `python scripts/run_dashboard.py --help` works
- [ ] `make dashboard` launches against the live repo artifacts
- [ ] `make test` passes
- [ ] Cytoscape is the active renderer for the graph surface
- [ ] Package labels are hidden by default
- [ ] The graph-first shell remains top bar / left sidebar / center graph / right inspector with the lower insight row beneath the graph
- [ ] Search, filters, and single-node selection still work after the renderer swap
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-032 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 5
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed showcase-track or renderer-track readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on Dashboard Redesign Stage 4, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- Do not slip into Stage 4 selection-workflow redesign under the label of Stage 3 renderer work
- Do not rewrite the renderer-agnostic data/view-model layers unless the renderer contract truly requires it
- Do not reintroduce the visible logo or move the lower insight panels back into the left rail
- Do not leave the repo in a half-Plotly / half-Cytoscape state without clear documentation of which renderer is active
