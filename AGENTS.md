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
2. `docs/handoff/CURRENT_STATUS.md`
3. `docs/handoff/NEXT_TASK.md`
4. `docs/specs/_INDEX.md`
5. Only the spec file(s) relevant to active task(s)

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
At completion of any task batch, agents must update both files:

1. `docs/handoff/CURRENT_STATUS.md`
2. `docs/handoff/NEXT_TASK.md`

Updates should be concrete, testable, and time-stamped.

## Documentation Conventions
- Specs live in `docs/specs/` with human-readable filenames (e.g., `graph-construction.md`).
- Every spec must be listed in `docs/specs/_INDEX.md` with summary, tags, and read triggers.
- `NEXT_TASK.md` should reference spec file paths directly whenever possible.

## Quality Bar
- Prefer reproducibility and explicit assumptions.
- Record decisions that affect outputs, schemas, or evaluation metrics.
- Keep changes small, reviewable, and aligned with milestone goals in `README.md`.
