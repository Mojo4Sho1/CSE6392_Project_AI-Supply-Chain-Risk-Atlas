# AGENTS.md

Operational guidance for coding agents working in this repository.

## Mission
Build and maintain a reproducible AI Supply Chain Risk Atlas pipeline as described in `README.md`.

## Environment
- Preferred environment: `conda` via `environment.yml`
- Environment name: `ai-supply-chain-risk-atlas`
- Default shell: `zsh`
- Prefer deterministic, scriptable steps over manual workflows

Environment setup:
- `conda env create -f environment.yml`
- `conda activate ai-supply-chain-risk-atlas`

## Required Read Order (Context-First)
Agents must follow this order to minimize context pollution:

1. `AGENTS.md` (this file)
2. `docs/handoff/QUICK_REFERENCE.md` (single-page cheat sheet — enums, schemas, CLI contract)
3. `docs/handoff/CURRENT_STATUS.md`
4. `docs/handoff/NEXT_TASK.md`
5. `docs/handoff/TASK_QUEUE.md` (prioritized backlog)
6. `docs/handoff/CAMPAIGN_PLAN.md` (long-horizon context)
7. `docs/specs/_INDEX.md`
8. Only the spec file(s) relevant to active task(s)

## New Agent Bootstrap Checklist
Use this checklist at the start of every new task batch:

1. Environment readiness
   - `conda env create -f environment.yml` (if env does not exist)
   - `conda activate ai-supply-chain-risk-atlas`
2. Context load
   - read files in the required read order above,
   - read `docs/specs/decision-log.md` before making policy assumptions.
3. Execution baseline
   - run from repository root,
   - use deterministic/scriptable workflows,
   - treat `data/models.csv` as human-owned input in v1.
4. Completion obligations
   - update `docs/handoff/CURRENT_STATUS.md`,
   - update `docs/handoff/NEXT_TASK.md`,
   - if any spec changes, update `docs/specs/_INDEX.md` in the same batch.

## Spec Loading Policy
- Do not read all specs by default.
- Use `docs/specs/_INDEX.md` as a routing table.
- Read only files and sections relevant to `NEXT_TASK.md`.
- When a spec is large, use targeted search first (e.g., `rg`) before loading full content.

## Task Execution Policy
- Treat `docs/handoff/NEXT_TASK.md` as the source of truth for immediate work.
- If tasks conflict with specs, pause and resolve ambiguity by updating handoff/specs explicitly.
- If tasks require behavior not covered by specs, add or update a spec first, then implement.

## Handoff Update Policy (Mandatory)
At completion of any task batch, agents must complete the "Mandatory final subtask" section at the bottom of `NEXT_TASK.md`. This is a checklist that includes:

1. Mark completed tasks as `done` in `docs/handoff/TASK_QUEUE.md`
2. Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md`
3. Rewrite `docs/handoff/CURRENT_STATUS.md` with concrete completed work, checks run, and any blockers
4. Rewrite `docs/handoff/NEXT_TASK.md` for the next agent using `docs/handoff/NEXT_TASK_TEMPLATE.md`
5. If any spec changed, update `docs/specs/_INDEX.md` in the same batch

The new `NEXT_TASK.md` must itself include the "Mandatory final subtask" section so the pattern propagates.
Updates should be concrete, testable, and time-stamped.

## Documentation Conventions
- Specs live in `docs/specs/` with human-readable filenames (e.g., `graph-construction.md`).
- Every spec must be listed in `docs/specs/_INDEX.md` with summary, tags, and read triggers.
- `NEXT_TASK.md` should reference spec file paths directly whenever possible.

## Automation and Token Efficiency
- When a task involves repeated commands (build, test, lint, scan, etc.), create a `Makefile`, shell script, or equivalent task runner so future agents can invoke it in one command instead of re-discovering the steps.
- Place reusable shell scripts in `scripts/` alongside pipeline scripts. Keep them minimal and idempotent.
- Be token-conscious: use targeted file reads, spec routing via `_INDEX.md`, and scripted workflows to avoid redundant context loading.

## Testing Policy
- Write unit tests and smoke tests for all new code. Place tests in `tests/` mirroring the source structure.
- After creating or modifying any code, run the full test suite (`pytest` from repo root) before considering the task complete. Do not skip this step.
- If a test fails, fix the issue before moving on. Do not leave the test suite in a broken state.
- See `docs/specs/testing-and-validation.md` for coverage requirements and milestone validation gates.

## Quality Bar
- Prefer reproducibility and explicit assumptions.
- Record decisions that affect outputs, schemas, or evaluation metrics.
- Keep changes small, reviewable, and aligned with milestone goals in `README.md`.
