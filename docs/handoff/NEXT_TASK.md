# Next Task

**Last updated:** 2026-03-26
**Owner:** Joe

## Task summary

Implement **Dashboard Redesign Stage 1: New App Shell, Layout, and Theme** from `docs/dashboard_redesign_plan.md`. This batch should turn the current stacked prototype into the graph-first shell described in the redesign plan while preserving the existing Plotly renderer and analytical behavior.

**Task queue references:** T-030 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Stage 0 is complete: theme tokens, branding asset routing, a layout module, and a controller layer now exist, so Stage 1 no longer needs to rediscover structure before changing the shell.
- The redesign plan explicitly says to implement one stage per batch, and Stage 1 is the first stage that should make the dashboard visibly feel like an application instead of a report page.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-030:** Read `docs/dashboard_redesign_plan.md` Stage 1 and `docs/dashboard_architecture_note.md` to align the new shell with the post-Stage-0 file split
2. **T-030:** Redesign the Dash layout in `scripts/_utils/dashboard_layout.py` around the graph-first shell: top bar, left sidebar, center graph region, right inspector
3. **T-030:** Update `scripts/_utils/dashboard_theme.py` and `assets/dashboard.css` to apply the dark-shell / light-canvas theme without changing dashboard semantics
4. **T-030:** Keep the current Plotly renderer working, extend tests as needed, then update handoff docs so Stage 2 can focus on branding polish rather than layout restructuring

## Scope (in)

- Dashboard Stage 1 only, as defined in `docs/dashboard_redesign_plan.md`
- A graph-first application shell with:
  - top bar
  - left control/sidebar area
  - center graph pane
  - right detail/inspector pane
- Theme updates needed for the dark shell and light graph canvas
- Compact metric cards and clearer panel grouping
- Tests for any changed layout/theme behavior
- Write unit tests and smoke tests for all new code (per `AGENTS.md` testing policy)

## Scope (out)

- Stage 2 branding experiments and logo placement polish
- Stage 3 Cytoscape migration
- Changes to the validated M1-M4 pipeline outputs or schemas
- Compare mode or multi-selection workflows
- Semantic changes to filters, search behavior, or dashboard data contracts unless a small presentation fix absolutely requires them

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `graphs/global.graphml`
  - `reports/summary.json`
  - `reports/summary.csv`
  - Stage 0 dashboard refactor:
    - `scripts/_utils/dashboard_theme.py`
    - `scripts/_utils/dashboard_controller.py`
    - `scripts/_utils/dashboard_layout.py`
    - `docs/dashboard_architecture_note.md`
- Specs (read only what's needed):
  - `docs/dashboard_redesign_plan.md` — authoritative Stage 1 layout/theme target
  - `docs/specs/dashboard-showcase.md` — current dashboard contract and renderer seam
  - `docs/handoff/CURRENT_STATUS.md` — exact Stage 0 completion state and verification caveats
  - `README.md` — documented launch flow and local-dashboard positioning

## Implementation notes

- Keep Plotly as the active renderer in this batch.
- Focus the visible redesign in `scripts/_utils/dashboard_layout.py`, `scripts/_utils/dashboard_theme.py`, and `assets/dashboard.css`.
- Preserve the Stage 0 data/view/controller split; do not re-collapse responsibilities into one module.
- Keep single-node selection and the existing read-only artifact contract.
- If port `8050` is occupied locally during manual verification, confirm the default command behavior first and then use a temporary alternate port for visual verification without changing the documented default.
- Run `make test` after code changes and treat expected failure paths as normal outcomes, not crashes.

## Acceptance criteria (definition of done)

- The dashboard uses a graph-first shell with top bar, left sidebar, center graph pane, and right inspector
- The shell uses the Stage 1 dark-theme direction while keeping a light graph canvas
- The graph is visually dominant above the fold and the page feels like an application rather than a report
- Existing analytical semantics and the Plotly renderer still work
- All tests pass (`make test`)
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `python scripts/run_dashboard.py --help` works
- [ ] `make dashboard` launches against the live repo artifacts
- [ ] `make test` passes
- [ ] The layout clearly maps to top bar / left sidebar / center graph / right inspector
- [ ] The shell is dark while the graph canvas remains light
- [ ] Plotly is still the active renderer
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-030 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 5
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed showcase-track or optional renderer-track readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on Dashboard Redesign Stage 2, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- Do not drift into Stage 2 branding polish under the label of Stage 1 shell work
- Do not break the current Plotly renderer or the existing filter/search/selection semantics while moving panels around
- Do not introduce Cytoscape in this batch; that remains a Stage 3 task
