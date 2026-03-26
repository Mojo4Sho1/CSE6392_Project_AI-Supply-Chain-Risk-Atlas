# Next Task

**Last updated:** 2026-03-26
**Owner:** Joe

## Task summary

Implement **Dashboard Redesign Stage 2: Branding Pass and Visual Refinement** from `docs/dashboard_redesign_plan.md`. This batch should polish the new Stage 1 shell with optional branding placement, clearer status styling, and more deliberate legend/empty-state/panel treatment while preserving the existing Plotly renderer and analytical behavior.

**Task queue references:** T-031 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Stage 1 is complete: the top bar / left sidebar / center graph / right inspector shell now exists, so Stage 2 can focus on visual cohesion instead of restructuring the app.
- The redesign plan explicitly separates branding polish from shell work, and this is the next bounded batch before the Stage 3 Cytoscape migration.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-031:** Read `docs/dashboard_redesign_plan.md` Stage 2, `docs/handoff/CURRENT_STATUS.md`, `docs/specs/dashboard-showcase.md`, and `assets/branding/README.md`
2. **T-031:** Make branding treatments and any logo placement easy to enable, disable, or relocate without hard-requiring a logo asset
3. **T-031:** Refine panel styling, badges, legend treatment, empty states, and microcopy in `scripts/_utils/dashboard_layout.py`, `scripts/_utils/dashboard_theme.py`, and `assets/dashboard.css`
4. **T-031:** Keep the current Plotly renderer working, extend tests as needed, then update handoff docs so Stage 3 can focus on Cytoscape instead of revisiting branding polish

## Scope (in)

- Dashboard Stage 2 only, as defined in `docs/dashboard_redesign_plan.md`
- Branding-safe shell refinements inside the existing Stage 1 structure
- Optional logo placement experiments or safe logo hooks
- Legend, badge, heading, and empty-state polish
- Small theme/layout refinements that improve cohesion without changing dashboard semantics
- Tests for any changed layout/theme/branding behavior
- Write unit tests and smoke tests for all new code (per `AGENTS.md` testing policy)

## Scope (out)

- Stage 3 Cytoscape migration
- Selection workflow redesign or compare mode
- Stage 5 linked-summary interaction work such as clickable summary tables
- Changes to validated M1-M4 pipeline outputs or schemas
- Large shell restructuring that effectively repeats Stage 1

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `graphs/global.graphml`
  - `reports/summary.json`
  - `reports/summary.csv`
  - Stage 1 dashboard shell:
    - `scripts/_utils/dashboard_layout.py`
    - `scripts/_utils/dashboard_theme.py`
    - `scripts/_utils/dashboard_render_plotly.py`
    - `assets/dashboard.css`
    - `assets/branding/README.md`
- Specs (read only what's needed):
  - `docs/dashboard_redesign_plan.md` — authoritative Stage 2 visual target
  - `docs/specs/dashboard-showcase.md` — current dashboard contract and shell expectations
  - `docs/handoff/CURRENT_STATUS.md` — exact Stage 1 completion state and verification caveats
  - `docs/dashboard_architecture_note.md` — file responsibility map after the Stage 0 refactor

## Implementation notes

- Keep Plotly as the active renderer in this batch.
- Treat the Stage 1 shell as the baseline; prefer polish over panel relocation.
- Any logo treatment must degrade cleanly when `assets/branding/ai_supply_chain_risk_atlas_logo.png` is absent.
- If port `8050` is occupied locally during manual verification, confirm the default command behavior first and then use a temporary alternate port without changing the documented default.
- Run `make test` after code changes and treat expected failure paths as normal outcomes, not crashes.

## Acceptance criteria (definition of done)

- The dashboard has a more cohesive branded identity without destabilizing the Stage 1 shell
- Logo placement, if introduced, is easy to enable/disable or relocate
- Legend, badges, headings, and empty states feel deliberate and readable
- Existing analytical semantics and the Plotly renderer still work
- All tests pass (`make test`)
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `python scripts/run_dashboard.py --help` works
- [ ] `make dashboard` launches against the live repo artifacts
- [ ] `make test` passes
- [ ] Branding treatment is safe when the logo asset is absent
- [ ] The graph-first shell remains top bar / left sidebar / center graph / right inspector
- [ ] Plotly is still the active renderer
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-031 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 5
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed showcase-track or optional renderer-track readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on Dashboard Redesign Stage 3, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- Do not drift into Stage 3 Cytoscape work under the label of Stage 2 polish
- Do not hard-wire branding to a required asset file or a single fixed logo placement
- Do not let new branding treatments crowd the graph or undo the graph-first shell delivered in Stage 1
