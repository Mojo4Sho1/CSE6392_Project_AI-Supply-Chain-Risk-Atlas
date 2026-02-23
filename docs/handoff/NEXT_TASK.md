# Next Task

**Last updated:** 2026-02-23  
**Owner:** Joe + Codex

## Task summary

Define the first authoritative spec documents for this project and register them in `docs/specs/_INDEX.md` so future agents can route context selectively.

## Why this task is next

- The operating workflow and handoff contract are now in place.
- Implementation work should not proceed without at least minimal authoritative specs.
- `_INDEX.md` is currently empty and cannot yet route task-to-spec selection.

## Scope (in)

- Create initial spec files with human-readable names in `docs/specs/` (exact filenames chosen during authoring).
- Document authoritative semantics for the first execution-critical areas, likely including:
  - model selection/snapshot rules,
  - ingestion + dependency artifact capture,
  - OSV normalization policy and output schema expectations.
- Register each created spec in `docs/specs/_INDEX.md` using:
  - `path`
  - `summary`
  - `tags`
  - `read-when`
- Update `AGENTS.md` once the exact conda environment name is finalized.

## Scope (out)

- Building the full extraction/graph/reporting pipeline.
- Running full benchmark/data collection jobs.
- Expanding into non-essential process docs beyond the minimum spec baseline.

## Dependencies / prerequisites

- Core project context:
  - `README.md`
  - `AGENTS.md`
- Routing index:
  - `docs/specs/_INDEX.md`
- Handoff control:
  - `docs/handoff/CURRENT_STATUS.md`

## Implementation notes

- Keep specs short and authoritative; avoid narrative duplication of `README.md`.
- Prefer explicit invariants, schemas, and decision rules over broad prose.
- Keep filenames human-readable; use index metadata for routing precision.

## Subtasks

- [ ] Create first set of spec files under `docs/specs/`.
- [ ] Add entries for each spec in `docs/specs/_INDEX.md` with tags and read triggers.
- [ ] Add concrete spec-path references in this `NEXT_TASK.md` for the next implementation pass.
- [ ] Finalize and record conda environment name in `AGENTS.md`.

## Acceptance criteria (definition of done)

- At least one authoritative spec exists and is ready for task routing.
- `_INDEX.md` maps current task areas to specific spec files without requiring full-spec ingestion.
- `NEXT_TASK.md` points to concrete spec paths instead of placeholder planning text.
- `AGENTS.md` environment field no longer contains `TBD` for conda env name.

## Verification checklist

- [ ] `find docs/specs -maxdepth 1 -type f` shows new spec files in addition to `_INDEX.md`.
- [ ] `rg -n "path|summary|tags|read-when" docs/specs/_INDEX.md`
- [ ] `rg -n "TBD" AGENTS.md` returns no conda-environment TODO.

## Risks / rollback notes

- Overly broad specs may create ambiguity and increase agent context load.
- Missing invariants in early specs can cause downstream rework in normalization/graph stages.
- If spec scope grows too fast, split into focused files and keep `_INDEX.md` routing granular.
