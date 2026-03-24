# Next Task

**Last updated:** 2026-03-24
**Owner:** Joe

## Task summary

Implement Phase 4 M4 reporting: build `scripts/generate_atlas_reports.py` so it reads `graphs/global.graphml` and writes `reports/summary.json`, `reports/summary.csv`, and reproducible figure outputs under `figures/`, then wire it into `make report` and `make all`.

**Task queue references:** T-019 through T-020 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Phase 3 is complete. `graphs/global.graphml` now exists and has been verified against the 13 normalized OSV inputs.
- The next open milestone gap is converting the graph into the baseline atlas metrics and report artifacts required for project completion.
- A separate local dashboard showcase track is now queued for post-M4 work; it should not delay the reporting batch.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-019:** Implement `scripts/generate_atlas_reports.py` + tests
2. **T-020:** Add `make report` and `make all` targets
3. Run end-to-end smoke verification on the current `graphs/global.graphml`

## Scope (in)

- Implement `scripts/generate_atlas_reports.py` that:
  - reads `graphs/global.graphml`,
  - computes the required baseline metrics from `docs/specs/graph-semantics-and-metrics.md`,
  - writes `reports/summary.json`,
  - writes `reports/summary.csv`,
  - writes reproducible figure output(s) under `figures/`
- Emit required `summary.json` fields from `docs/specs/artifact-schemas.md`:
  - `global_metrics`
  - `per_model_metrics`
  - `reused_vulnerable_packages`
- Keep report ordering deterministic and define stable tie-breaks in code/tests
- Write unit tests and smoke tests for all new code (per `AGENTS.md` testing policy)
- Create or extend `Makefile` targets for repeated commands (per `AGENTS.md` automation policy)
- Keep the implementation decision-complete with the clarified report contract below; do not invent additional metrics unless the specs are updated in the same batch

## Scope (out)

- Composite risk scoring
- New graph edge types or graph schema changes unless a genuine spec gap is discovered
- Re-running M1 through M3 except when needed to debug a report-input contract issue
- Dashboard implementation; that work is tracked separately in `T-023` through `T-025`

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `graphs/global.graphml`
  - `osv/<model_id>/normalized.json` only if cross-checking a metric is helpful during debugging
- Specs (read only what's needed):
  - `docs/specs/graph-semantics-and-metrics.md` — required baseline metrics and graph semantics
  - `docs/specs/artifact-schemas.md` — required `reports/summary.json` fields
  - `docs/specs/pipeline-execution-contract.md` — shared CLI contract and determinism expectations
  - `docs/specs/testing-and-validation.md` — report coverage requirements and M4 validation gate

## Implementation notes

- Package-node vulnerability IDs are stored in GraphML as `vuln_ids_json`; reporting must parse that field back into a list before computing unique-vulnerability metrics
- Model nodes include `model_id`, `hf_model_id`, and `snapshot_timestamp_utc`; do not derive per-model identity from opaque GraphML node IDs
- `reports/summary.csv` should mirror `summary.json.per_model_metrics` exactly, with one row per model and these columns in order:
  - `hf_model_id`
  - `model_id`
  - `vulnerable_direct_dependencies`
  - `vulnerable_transitive_dependencies`
  - `vulnerable_packages_per_model`
  - `unique_vuln_ids_per_model`
- Deterministic ordering rules:
  - `per_model_metrics` / `summary.csv` rows sorted by `hf_model_id`, then `model_id`
  - `reused_vulnerable_packages` sorted by `impacted_model_count` descending, then `ecosystem`, `name`, `version`
- Baseline metrics only:
  - unique package count
  - average packages per model
  - average direct packages per model
  - average transitive packages per model
  - vulnerable direct dependencies per model
  - vulnerable transitive dependencies per model
  - vulnerable packages per model
  - unique vulnerability IDs per model
  - reused vulnerable packages / impacted-model counts
- Minimum acceptable v1 figure set:
  - `figures/reused_vulnerable_packages.png` — ranked bar chart of the top reused vulnerable packages
  - `figures/impacted_model_count_distribution.png` — distribution of impacted-model counts per vulnerable package
- `make report` should call `scripts/generate_atlas_reports.py` against `graphs/global.graphml`
- `make all` should reuse the existing stage targets so one `make` invocation carries a single shared `TIMESTAMP`
- Current Phase 4 input sanity baseline for the repo:
  - `graphs/global.graphml` currently contains 13 model nodes, 276 package nodes, and 322 `uses_package` edges
- Run `pytest` / `make test` after every code change
- Treat expected failure paths as normal outcomes, not crashes

## Acceptance criteria (definition of done)

- `python scripts/generate_atlas_reports.py --help` works
- `make report` runs the reporting script
- `make all` runs the full pipeline end-to-end
- `reports/summary.json` and `reports/summary.csv` are produced and contain the required baseline metrics
- `figures/` contains at least the two expected reproducible PNG outputs
- All tests pass (`make test`)
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `python scripts/generate_atlas_reports.py --help` works
- [ ] `make report` completes without error
- [ ] `make all` completes without error
- [ ] `reports/summary.json` exists and contains the required top-level fields
- [ ] `reports/summary.csv` exists and includes one row per model
- [ ] `figures/reused_vulnerable_packages.png` exists
- [ ] `figures/impacted_model_count_distribution.png` exists
- [ ] `make test` passes
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-019 through T-020 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 4
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed milestone checklist state, acceptance gates, or cross-phase verification readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on Phase 5 validation/documentation, following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- GraphML scalar typing can turn numbers/bools into strings on load; parse and normalize values before metric calculations
- Ranking/order-sensitive outputs need deterministic tie-breaks so repeated runs stay reproducible
- Keep figure generation simple and scriptable; avoid notebook-only workflows or interactive-only render paths
