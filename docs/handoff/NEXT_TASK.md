# Next Task

**Last updated:** 2026-03-24
**Owner:** Joe

## Task summary

Implement Phase 3 M3 graph construction: build `scripts/build_risk_graph.py` so it reads the normalized OSV outputs in `osv/` and writes the global typed atlas graph to `graphs/global.graphml`, then wire it into `make graph`.

**Task queue references:** T-017 through T-018 (see `docs/handoff/TASK_QUEUE.md`)

## Why this task is next

- Phase 2 is complete. All 13 manifest directories now have paired `osv/<model_id>/raw.json` and `osv/<model_id>/normalized.json` outputs.
- The next open milestone gap is converting those normalized package records into the v1 graph structure required for downstream reporting.

Long-horizon reference:
- `docs/handoff/CAMPAIGN_PLAN.md` (phased roadmap)
- `docs/handoff/PROJECT_CHECKLIST.md` (milestone gates)

## Recommended task order

1. **T-017:** Implement `scripts/build_risk_graph.py` + tests
2. **T-018:** Add `make graph` target to `Makefile`
3. Run end-to-end smoke verification on the current `osv/` corpus

## Scope (in)

- Implement `scripts/build_risk_graph.py` that:
  - reads `osv/<model_id>/normalized.json`,
  - creates `Model` and `Package` nodes with required attributes,
  - creates `uses_package` edges from models to packages,
  - deduplicates package nodes by `(ecosystem, name, version)`,
  - writes `graphs/global.graphml`
- Preserve models that have zero normalized packages (for example `stabilityai/stable-diffusion-xl-base-1.0`) as model nodes with zero `uses_package` edges
- Write unit tests and smoke tests for all new code (per `AGENTS.md` testing policy)
- Create or extend `Makefile` targets for repeated commands (per `AGENTS.md` automation policy)

## Scope (out)

- Reporting and atlas metrics generation (Phase 4)
- Adding `depends_on` edges; those remain deferred in v1
- Re-running M1 or M2 unless needed to debug a graph input contract issue

## Dependencies / prerequisites

- Quick orientation: `docs/handoff/QUICK_REFERENCE.md`
- Environment: `environment.yml`, `AGENTS.md`
- Inputs from prior phase:
  - `osv/<model_id>/normalized.json`
  - `manifests/<model_id>/manifest_index.json` if provenance cross-checks are helpful
- Specs (read only what's needed):
  - `docs/specs/graph-semantics-and-metrics.md` — required node/edge semantics and baseline graph rules
  - `docs/specs/artifact-schemas.md` — package field schema and report-facing graph inputs
  - `docs/specs/pipeline-execution-contract.md` — shared CLI contract, exit codes, determinism
  - `docs/specs/testing-and-validation.md` — graph test coverage and M3 validation gate

## Implementation notes

- Required node types in v1 are `Model` and `Package`
- Required edge type in v1 is `uses_package`; do not implement `depends_on`
- Package identity is strictly `(ecosystem, name, version)`; do not duplicate package nodes across models when those three values match
- Edge attributes must include `dependency_scope`, `depth`, and `manifest_source`
- `depth` is not explicitly specified elsewhere; choose a deterministic v1 rule, document it in code/tests, and keep it stable
- Some normalized inputs contain transitive dependencies; others contain only direct dependencies
- Run `pytest` / `make test` after every code change
- Treat expected failure paths as normal outcomes, not crashes

## Acceptance criteria (definition of done)

- `python scripts/build_risk_graph.py --help` works; CLI flags match the common contract
- `make graph` runs the graph build script
- `graphs/global.graphml` is produced and loads successfully
- Graph contents match normalized inputs:
  - one model node per normalized file
  - package nodes deduplicated by `(ecosystem, name, version)`
  - `uses_package` edges preserve `dependency_scope` and `manifest_source`
- All tests pass (`make test`)
- Handoff docs updated (see mandatory final subtask below)

## Verification checklist

- [ ] `python scripts/build_risk_graph.py --help` works
- [ ] `make graph` completes without error
- [ ] `graphs/global.graphml` exists and loads cleanly
- [ ] Package deduplication matches the normalized inputs
- [ ] A model with zero packages still appears in the graph with zero `uses_package` edges
- [ ] `make test` passes
- [ ] No unresolved placeholder text in new code/docs

## Mandatory final subtask: Update handoff documentation

**Complete this last, after all code is written and all tests pass.**

Using `docs/handoff/NEXT_TASK_TEMPLATE.md` as a guide, update the following before closing this batch:

- [ ] Mark T-017 through T-018 as `done` in `docs/handoff/TASK_QUEUE.md`
- [ ] Tick completed checkboxes in `docs/handoff/CAMPAIGN_PLAN.md` Phase 3
- [ ] Update `docs/handoff/PROJECT_CHECKLIST.md` if this batch changed milestone checklist state, acceptance gates, or cross-phase verification readiness
- [ ] Rewrite `docs/handoff/CURRENT_STATUS.md`:
  - what was completed (concrete, verifiable)
  - checks run and their outcomes
  - any remaining blockers or caveats
- [ ] Rewrite `docs/handoff/NEXT_TASK.md` to brief the next agent on Phase 4 (M4 reporting), following `NEXT_TASK_TEMPLATE.md`
- [ ] If any spec changed during this batch, update `docs/specs/_INDEX.md`

The next `NEXT_TASK.md` must itself include this same "Mandatory final subtask" section so the pattern propagates to every future agent.

## Risks / rollback notes

- `depth` on `uses_package` edges is not fully specified outside the graph spec; pick one deterministic rule and keep tests explicit
- GraphML serialization can be sensitive to attribute typing; verify the produced file reloads before closing the batch
- Preserve empty-package models in the graph so later reporting can distinguish “no dependencies found” from “model missing from graph”
