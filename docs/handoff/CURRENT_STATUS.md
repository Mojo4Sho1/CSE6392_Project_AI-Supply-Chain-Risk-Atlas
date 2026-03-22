# Current Status

**Last updated:** 2026-03-21
**Owner:** Joe

## Current focus

Phase 0 scaffolding complete. Project is ready for Phase 1 (M1 ingestion implementation).

## Completed in current focus

- CSV/spec reconciliation (DEC-008):
  - removed 4 low-value columns from `data/models.csv`: `ranking_signal`, `selection_method`, `eligible`, `selection_source`
  - kept `selection_rationale` (unique per-model provenance)
  - added `dependency_artifact` and `dependency_artifact_url` as official optional hint columns
  - updated `data-sourcing-and-eligibility.md` and `artifact-schemas.md` to match
  - recorded decision in `decision-log.md` as DEC-008
- Agent scaffolding:
  - created `docs/handoff/CAMPAIGN_PLAN.md` — phased roadmap (Phase 0–5)
  - created `docs/handoff/TASK_QUEUE.md` — prioritized task backlog with 22 tasks across all phases
  - created `docs/handoff/QUICK_REFERENCE.md` — single-page cheat sheet (CSV schema, enums, CLI contract, file layout)
  - added Automation/Testing policies to `AGENTS.md`
  - created `CLAUDE.md` for Claude Code orientation

## Passing checks

- `data/models.csv` has 9 columns matching spec (13 candidate rows)
- All spec files consistent with CSV schema after DEC-008
- `docs/specs/_INDEX.md` routes to all 7 active specs
- Decision log has 8 accepted entries, all current
- Campaign plan, task queue, and quick reference all present

## Known gaps/blockers

- No implementation code exists yet (scripts/, tests/)
- No Makefile exists yet
- OSV-Scanner not yet verified in conda env
- CSV has 13 candidates; target is 15 (2 more may be added later)

## Active coordination notes

- Phase 1 tasks (T-007 through T-013) are all `queued` and ready
- Next agent should start with T-007 (model_id normalization) or T-008 (CSV parser)
- T-007 and T-008 have no interdependencies and can be worked in parallel

## Next task (single target)

Begin Phase 1 M1 implementation. See `NEXT_TASK.md` for details and `TASK_QUEUE.md` for the full backlog.

## Definition of done for next task

See `NEXT_TASK.md` acceptance criteria and `TASK_QUEUE.md` per-task acceptance criteria.
