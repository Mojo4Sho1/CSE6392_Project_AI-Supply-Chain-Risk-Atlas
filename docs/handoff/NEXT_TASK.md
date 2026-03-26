# Next Task

**Last updated:** 2026-03-26
**Owner:** Joe

## Task summary

Evaluate the newly implemented Plotly dashboard against the live project artifacts and decide whether the renderer is good enough to keep, or whether the project should open an optional Cytoscape follow-on batch.

**Task queue references:** T-026 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- The Plotly dashboard is now implemented, tested, documented, and verified on the live graph/report artifacts.
- The renderer seam was added intentionally, so the next decision is product-facing rather than architectural: keep Plotly or invest in Cytoscape.
- This decision should be made from the real dashboard experience, not from speculation, so it is best handled as a short evaluation batch before any renderer rewrite.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-026:** Launch the live dashboard against the current repo artifacts and record concrete strengths, pain points, and any visual limitations of the Plotly renderer
2. **T-026:** Compare the live dashboard behavior against `docs/specs/dashboard-showcase.md` and the Cytoscape migration goals already discussed
3. **T-026:** Update handoff/task docs with an explicit recommendation: keep Plotly as-is, or proceed to Cytoscape

## Scope (in)

- Launch and review the implemented dashboard with the current live artifacts
- Capture concrete visual/interaction findings grounded in the real dashboard behavior
- Decide whether Cytoscape would meaningfully improve the demo enough to justify a follow-on batch
- If the answer is yes, update the handoff/task docs so T-027 is immediately executable

## Scope (out)

- Re-implementing the dashboard from scratch
- Immediate Cytoscape implementation in the same batch unless the evaluation explicitly approves that follow-on
- Changes to the validated M1-M4 pipeline outputs or schemas

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `graphs/global.graphml`
  - `reports/summary.json`
  - `reports/summary.csv`
  - the implemented Plotly dashboard launched by `make dashboard`
  - `paper/final_report.tex` for later write-up integration once the dashboard recommendation is settled
- Specs (read only what's needed):
  - `docs/specs/dashboard-showcase.md` — current dashboard contract and future renderer seam
  - `docs/handoff/CURRENT_STATUS.md` — exact implementation status and verification outcomes
  - `README.md` — documented launch flow and showcase framing

## Implementation notes

- Use the live dashboard, not just code inspection, to judge whether Plotly is sufficient
- If opening T-027, keep the existing data/view layer intact and frame the next batch strictly as a renderer swap
- Avoid speculative renderer churn; record concrete reasons tied to the current UX
- Write the dashboard recommendation so it can later be folded directly into `paper/final_report.tex` without another round of interpretation

## Acceptance criteria (definition of done)

- The repo contains a written, concrete recommendation: keep Plotly or proceed to Cytoscape
- The recommendation is grounded in the live dashboard behavior and references specific strengths/limitations
- If Cytoscape is recommended, the backlog/handoff docs are updated so T-027 is immediately executable
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `make dashboard` launches against the live repo artifacts
- [ ] The evaluation records concrete Plotly strengths and limitations
- [ ] The keep-vs-Cytoscape recommendation is explicit, not implicit
- [ ] `docs/handoff/TASK_QUEUE.md` and `docs/handoff/NEXT_TASK.md` reflect the recommendation cleanly
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-026 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 5
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed showcase-track or optional renderer-track readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on the next queued batch after renderer evaluation, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- Avoid turning a short product evaluation into an unplanned renderer rewrite
- Judge the current dashboard from the real local demo, not from the code alone
- If Cytoscape is deferred, say so explicitly so the backlog does not stay ambiguous
