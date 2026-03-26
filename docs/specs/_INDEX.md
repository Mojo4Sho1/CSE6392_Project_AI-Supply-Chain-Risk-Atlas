# Specs Index

Purpose: route agents to only the specification documents needed for the current task.

## How to Use
1. Read `docs/handoff/NEXT_TASK.md`.
2. If planning across phases, read `docs/handoff/PROJECT_CHECKLIST.md`.
3. Read `docs/specs/decision-log.md` before interpreting policy defaults.
4. Match task scope to entries below.
5. Open only relevant spec files/sections.
6. Add new specs here immediately when created.

## Entry Format
- `path`: spec file path
- `summary`: what the document defines
- `tags`: routing keywords
- `read-when`: explicit trigger for loading this spec

## Specs
- `path`: `docs/specs/data-sourcing-and-eligibility.md`
- `summary`: authoritative human-curated candidate CSV schema and strict eligibility rules for model repositories.
- `tags`: `model-selection`, `eligibility`, `manifest`, `data-sourcing`
- `read-when`: tasks involve selecting model candidates, validating `models.csv` schema, evaluating repo eligibility, or deciding exclusions.

- `path`: `docs/specs/extraction-and-normalization.md`
- `summary`: contract for artifact acquisition, OSV raw output handling, and normalized vulnerability schema.
- `tags`: `ingestion`, `osv`, `normalization`, `schema`
- `read-when`: tasks involve fetching dependency artifacts, scanning vulnerabilities, or writing normalized outputs.

- `path`: `docs/specs/graph-semantics-and-metrics.md`
- `summary`: graph node/edge semantics, GraphML-safe typing/merge rules, and required baseline metrics for atlas evaluation.
- `tags`: `graph`, `metrics`, `networkx`, `risk-structure`
- `read-when`: tasks involve graph construction, edge rules, deduplication identity, or reporting metrics.

- `path`: `docs/specs/artifact-schemas.md`
- `summary`: normative schema contracts for pipeline artifacts, canonical enums, timestamp rules, and deterministic `model_id` normalization.
- `tags`: `schema`, `contracts`, `manifest`, `osv`, `reports`
- `read-when`: tasks produce or consume `manifest_index.json`, normalized OSV outputs, report summaries, or need canonical enums and `model_id` normalization rules.

- `path`: `docs/specs/pipeline-execution-contract.md`
- `summary`: canonical script boundaries, shared CLI contract, exit codes, retry policy, idempotency, and determinism requirements.
- `tags`: `execution`, `cli`, `idempotency`, `retries`, `runtime`
- `read-when`: tasks implement or modify pipeline scripts, operational behavior, or run-level error handling.

- `path`: `docs/specs/testing-and-validation.md`
- `summary`: required unit/integration/smoke coverage and milestone validation gates.
- `tags`: `testing`, `validation`, `fixtures`, `reproducibility`
- `read-when`: tasks add code, adjust contracts, or define acceptance criteria/check commands.

- `path`: `docs/specs/decision-log.md`
- `summary`: accepted policy defaults and change-control rules for previously open project decisions.
- `tags`: `policy`, `defaults`, `governance`, `decisions`
- `read-when`: any task depends on policy choices such as sample sizing, unpinned handling, or required graph edges.

- `path`: `docs/specs/dashboard-showcase.md`
- `summary`: local single-page Dash + Plotly showcase dashboard contract, including the graph-first shell, lower insight row, Hugging Face-first/no-logo presentation direction, swap-friendly renderer seam, required inputs/views/interactions, and runtime defaults.
- `tags`: `dashboard`, `showcase`, `ui`, `dash`, `plotly`
- `read-when`: tasks involve the interactive local demo app, dashboard data/view/render layering, UI behavior, or `make dashboard`.

When adding another spec, use this template:

- `path`: `docs/specs/<filename>.md`
- `summary`: <one to two sentence authoritative scope>
- `tags`: `<tag1>`, `<tag2>`, `<tag3>`
- `read-when`: <specific condition>
