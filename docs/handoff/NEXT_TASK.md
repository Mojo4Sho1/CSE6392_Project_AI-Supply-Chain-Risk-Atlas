# Next Task

**Last updated:** 2026-03-26
**Owner:** Joe

## Task summary

Implement **Dashboard Redesign Stage 0: Audit and Refactor Preparation** from `docs/dashboard_redesign_plan.md`. This batch should preserve the current dashboard behavior while reorganizing the codebase just enough to make the later shell/theme/Cytoscape stages clean and low-risk.

**Task queue references:** T-029 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- The live dashboard has already been reviewed, and the redesign direction is now explicitly documented in `docs/dashboard_redesign_plan.md`.
- Stage 0 is the first execution step in that staged roadmap and unblocks all later UI work.
- The redesign plan explicitly says not to combine major stages, so this batch should focus on preparation rather than visible redesign.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-029:** Read `docs/dashboard_redesign_plan.md` and map the current dashboard files to the staged redesign responsibilities
2. **T-029:** Introduce a dedicated place for theme tokens / design constants and a clear branding asset location
3. **T-029:** Refactor or annotate the current dashboard code so data transformation, rendering, layout, and future theme/branding work are easier to change independently
4. **T-029:** Keep the current Plotly dashboard working, then update handoff docs so the next batch can start directly on Stage 1

## Scope (in)

- Dashboard Stage 0 only, as defined in `docs/dashboard_redesign_plan.md`
- Theme / token organization for colors, spacing, and typography constants
- Clear branding asset path support
- Light structural cleanup or developer notes that make later stages easier
- Preserve existing Plotly behavior and analytical semantics
- Write unit tests for any code changes and keep launch/test workflows one-command simple

## Scope (out)

- Stage 1 layout redesign
- Stage 2 branding polish
- Stage 3 Cytoscape migration
- Changes to validated M1-M4 pipeline outputs or schemas
- Any new compare mode or multi-selection workflow

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `graphs/global.graphml`
  - `reports/summary.json`
  - `reports/summary.csv`
  - the implemented Plotly dashboard launched by `make dashboard`
  - `paper/final_report.tex` for later write-up integration once the dashboard recommendation is settled
  - `docs/dashboard_redesign_plan.md`
- Specs (read only what's needed):
  - `docs/dashboard_redesign_plan.md` — authoritative staged redesign roadmap
  - `docs/specs/dashboard-showcase.md` — current dashboard contract and future renderer seam
  - `docs/handoff/CURRENT_STATUS.md` — exact implementation status and verification outcomes
  - `README.md` — documented launch flow and current repo layout

## Implementation notes

- Keep Dash and the current Plotly renderer in place for this batch.
- Do not drift into visible Stage 1 shell redesign unless a very small presentation tweak is necessary to support the refactor.
- Preserve the existing data/view/render seam and make it easier to theme, restyle, and later swap the renderer.
- Reuse `make dashboard` and `make test`; only add new automation if Stage 0 introduces a repeated workflow that is not already one-command.
- Run `make test` after code changes and treat expected failure paths as normal outcomes, not crashes.

## Acceptance criteria (definition of done)

- A dedicated place for dashboard theme values exists
- Branding assets have a clear home and can be introduced without ad hoc file placement
- The current dashboard still launches with the documented defaults
- The codebase is organized clearly enough that Stage 1 can focus on layout/theme rather than rediscovering structure
- All tests pass (`make test`)
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `python scripts/run_dashboard.py --help` works
- [ ] `make dashboard` launches against the live repo artifacts
- [ ] `make test` passes
- [ ] Theme / token organization exists in the codebase
- [ ] Branding asset location is documented or scaffolded clearly
- [ ] `docs/handoff/TASK_QUEUE.md` and `docs/handoff/NEXT_TASK.md` point cleanly to Stage 1 afterward
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-029 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 5
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed showcase-track or optional renderer-track readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on Dashboard Redesign Stage 1, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- Avoid accidentally implementing Stage 1 layout work under the label of Stage 0 refactoring
- Do not break the current Plotly dashboard while reorganizing code for later stages
- Do not introduce Cytoscape in this batch; that is explicitly deferred to Stage 3
