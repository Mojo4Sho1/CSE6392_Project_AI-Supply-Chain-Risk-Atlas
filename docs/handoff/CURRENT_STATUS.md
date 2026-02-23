# Current Status

**Last updated:** 2026-02-23  
**Owner:** Joe + Codex

## Current focus

Translate planning decisions into authoritative project specs and shared environment setup.

## Completed in current focus

- Created shared conda definition file:
  - `environment.yml` with initial Python/data/graph/analysis dependencies.
- Added starter candidate manifest:
  - `data/models.csv` with required header schema.
- Authored and registered first authoritative specs:
  - `docs/specs/data-sourcing-and-eligibility.md`
  - `docs/specs/extraction-and-normalization.md`
  - `docs/specs/graph-semantics-and-metrics.md`
  - Added entries in `docs/specs/_INDEX.md` with `summary`, `tags`, and `read-when`.
- Added explicit deferred-policy markers in specs via `OPEN_DECISION` sections for:
  - unpinned dependency vulnerability policy,
  - `depends_on` edge requirement level,
  - composite risk score decision.
- Updated operating docs to align with new setup:
  - `AGENTS.md` now includes concrete conda environment name and setup commands.
  - `README.md` now reflects `environment.yml`, `data/models.csv`, and agent workflow/read order.

## Passing checks

- Required planning artifacts now exist:
  - `environment.yml`
  - `data/models.csv`
  - `docs/specs/data-sourcing-and-eligibility.md`
  - `docs/specs/extraction-and-normalization.md`
  - `docs/specs/graph-semantics-and-metrics.md`
- `docs/specs/_INDEX.md` now routes to concrete spec files.
- `AGENTS.md` no longer contains conda environment `TBD`.

## Known gaps/blockers

- Model sampling policy is not finalized (manual curation vs automated ranking).
- Ingestion contract is specified, but no script implementation exists yet.
- Multiple `OPEN_DECISION` items remain intentionally unresolved until more data is available.

## Active coordination notes

- The ingestion spec intentionally defines a contract only; no extraction script has been implemented.
- Strict eligibility is now the default policy for initial pipeline iterations.
- Next implementation should start from `data/models.csv` and produce reproducible artifact/provenance logs.

## Next task (single target)

Implement a minimal ingestion + eligibility script from the contract spec that reads `data/models.csv` and writes per-model manifest indexes/outcome metadata.

## Definition of done for next task

- Script exists (initial version) and follows the contract in `docs/specs/extraction-and-normalization.md`.
- Script reads `data/models.csv` and emits deterministic per-model outputs under `manifests/<model_id>/`.
- Eligibility pass/fail outcomes are explicit with machine-readable reasons.
- `NEXT_TASK.md` is updated to point to the subsequent OSV-scan integration step.
