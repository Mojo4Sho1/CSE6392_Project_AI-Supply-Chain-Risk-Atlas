# Next Task

**Last updated:** 2026-03-24
**Owner:** Joe

## Task summary

Complete the Phase 5 validation/documentation batch: run the cross-phase verification suite against the now-complete M1-M4 pipeline, then reconcile README/handoff/spec references so the repository is submission-ready and internally consistent.

**Task queue references:** T-021 through T-022 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Phase 4 is complete: `reports/summary.json`, `reports/summary.csv`, and the required figures now exist and `make all` completes successfully.
- The remaining core project gap is Phase 5 validation and documentation: confirm milestone gates/cross-phase checks, then align README and handoff docs with the final pipeline state.
- The dashboard showcase remains a separate post-validation track and should not delay this batch.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-021:** Run the Phase 5 validation pass and record exact outcomes against `PROJECT_CHECKLIST.md`
2. **T-022:** Reconcile README/handoff/spec references and remove stale project-state language
3. Re-run the final verification commands after any documentation/code adjustments

## Scope (in)

- Run the explicit Phase 5 validation checks for the completed M1-M4 pipeline and capture results in docs:
  - milestone gates in `docs/handoff/PROJECT_CHECKLIST.md`
  - cross-phase verification suite items that can be checked locally now
  - documentation consistency checks from `docs/specs/testing-and-validation.md`
- Perform the final documentation pass:
  - README accuracy
  - handoff docs current and mutually consistent
  - spec references and task references not stale
- Make any small corrective edits required to satisfy validation or documentation consistency findings
- Write tests for any code changed during this batch (per `AGENTS.md` testing policy)
- Create or extend `Makefile` targets for repeated commands if the validation batch reveals another repeated workflow

## Scope (out)

- Dashboard implementation; that work is tracked separately in `T-023` through `T-025`
- New report metrics or schema changes unless the validation pass finds a genuine contract gap
- Broad feature expansion beyond validation, cleanup, and documentation readiness

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `manifests/<model_id>/manifest_index.json`
  - `osv/<model_id>/normalized.json`
  - `graphs/global.graphml`
  - `reports/summary.json`
  - `reports/summary.csv`
  - `figures/reused_vulnerable_packages.png`
  - `figures/impacted_model_count_distribution.png`
- Specs (read only what's needed):
  - `docs/specs/testing-and-validation.md` — required validation/documentation consistency checks and milestone gates
  - `docs/specs/pipeline-execution-contract.md` — end-to-end CLI/runtime expectations for the full pipeline
  - `docs/specs/artifact-schemas.md` — output boundary contracts when cross-checking artifacts
  - `docs/specs/decision-log.md` — confirm docs still reflect locked v1 defaults

## Implementation notes

- The current verified local baseline is:
  - `make test` -> **114 passed**
  - `make report` -> rewrites Phase 4 outputs successfully
  - `make all` -> completes successfully
- `make all` now reuses the stage chain and may short-circuit on existing outputs; if you intentionally need a full regeneration, use `make clean` first
- Keep documentation concrete and time-stamped; when referencing current artifact baselines, prefer exact counts already verified in `CURRENT_STATUS.md`
- If the validation pass uncovers a contract gap, update the relevant spec before changing behavior
- Run `pytest` / `make test` after every code change
- Treat expected failure paths as normal outcomes, not crashes

## Acceptance criteria (definition of done)

- The Phase 5 validation results are recorded concretely in handoff/project docs
- README and handoff/spec references are current and consistent with the implemented M1-M4 pipeline
- Any issues found during validation are either fixed in this batch or documented as explicit blockers/caveats
- All tests pass (`make test`)
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `make all` passes
- [ ] `make test` passes
- [ ] Phase 5 milestone/checklist state is updated in `docs/handoff/PROJECT_CHECKLIST.md`
- [ ] Documentation consistency checks pass (`rg -n "OPEN_DECISION" docs/specs README.md docs/handoff --glob '!docs/specs/testing-and-validation.md'`)
- [ ] README accurately describes the completed pipeline outputs and execution path
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-021 through T-022 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 5
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed milestone checklist state, acceptance gates, or cross-phase verification readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on the next queued batch after validation/docs, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- Validation work can uncover stale README/spec references that look minor but change project interpretation; reconcile them carefully against the decision log
- Because `make all` can now reuse existing artifacts, use `make clean` before claiming a full regeneration from scratch
- Keep the dashboard showcase track deferred until the validation/docs batch is truly complete
