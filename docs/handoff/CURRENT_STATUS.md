# Current Status

**Last updated:** 2026-02-23  
**Owner:** Joe + Codex

## Current focus

Establish the agent-first operating workflow for this repository: read order, handoff contract, and spec-routing index.

## Completed in current focus

- Created root-level `AGENTS.md` with:
  - mandatory read order (`AGENTS -> CURRENT_STATUS -> NEXT_TASK -> _INDEX -> relevant specs only`),
  - selective spec-loading policy,
  - mandatory handoff update policy.
- Created `docs/specs/_INDEX.md` with:
  - routing-oriented entry format (`path`, `summary`, `tags`, `read-when`),
  - usage guidance for loading only relevant specs.
- Created handoff control files:
  - `docs/handoff/CURRENT_STATUS.md`
  - `docs/handoff/NEXT_TASK.md`
- Captured bootstrap next tasks for defining the first authoritative specs.

## Passing checks

- Required docs scaffold exists:
  - `AGENTS.md`
  - `docs/specs/_INDEX.md`
  - `docs/handoff/CURRENT_STATUS.md`
  - `docs/handoff/NEXT_TASK.md`
- Read-order policy in `AGENTS.md` matches agreed handoff-first workflow.
- `_INDEX.md` currently has no registered specs and is ready for first entries.

## Known gaps/blockers

- Project conda environment name is still TBD in `AGENTS.md`.
- No authoritative specs have been authored yet under `docs/specs/`.
- `_INDEX.md` has structure but no active spec registrations yet.

## Active coordination notes

- Handoff-first context loading is now explicit and should minimize token/context waste.
- Spec filenames are expected to stay human-readable; stable IDs can be added in `_INDEX.md` when needed.
- Temporary template reference files were used for style alignment and are now removed from active handoff flow.

## Next task (single target)

Create and register the first authoritative spec set in `docs/specs/` and align `NEXT_TASK.md` task references to those specs.

## Definition of done for next task

- At least one authoritative spec exists in `docs/specs/` with clear scope and invariants.
- New spec file(s) are registered in `docs/specs/_INDEX.md` with tags and read triggers.
- `docs/handoff/NEXT_TASK.md` references concrete spec paths for upcoming implementation work.
