# NEXT_TASK.md Template

Use this template when writing the next agent's task brief as part of the mandatory handoff subtask. Replace all `<placeholder>` values. Delete sections that don't apply. Keep it scannable — the next agent must be able to load this file and immediately know what to do.

---

```markdown
# Next Task

**Last updated:** <YYYY-MM-DD>
**Owner:** Joe

## Task summary

<One or two sentences describing the work. State the script/module being built and its output.>

**Task queue references:** <T-XXX through T-XXX> (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- <What was completed in the prior batch that unblocks this one.>
- <What gap or milestone gate this batch addresses.>

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

<List subtasks in order. Note any that can be run in parallel.>

1. **<T-XXX>:** <description>
2. **<T-XXX>:** <description>
...

## Scope (in)

- <Concrete deliverable 1>
- <Concrete deliverable 2>
- Write unit tests and smoke tests for all new code (per `AGENTS.md` testing policy).
- Create or extend `Makefile` targets for any repeated commands (per `AGENTS.md` automation policy).

## Scope (out)

- <Explicitly excluded work, with brief reason.>

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase: <list output files produced by prior batch>
- Specs (read only what's needed):
  - `docs/specs/<spec>.md` — <why>
  - `docs/specs/<spec>.md` — <why>

## Implementation notes

- <Key constraint or gotcha the agent must know.>
- Run `pytest` / `make test` after every code change.
- Treat expected failure paths as normal outcomes, not crashes.

## Acceptance criteria (definition of done)

- <Verifiable criterion 1>
- <Verifiable criterion 2>
- All tests pass (`make test`).
- Handoff docs updated (see mandatory final subtask below).

## Verification checklist

- [ ] `python scripts/<script>.py --help` works
- [ ] `make test` passes
- [ ] <Output file> produced and validates against schema
- [ ] <Negative-path fixture> fails with expected exit code / reason code
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark <T-XXX through T-XXX> as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase <N>
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed milestone checklist state, acceptance gates, or cross-phase verification readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on <next phase/task>, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- <Risk 1 and mitigation.>
- <Risk 2 and mitigation.>
```
