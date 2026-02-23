# Specs Index

Purpose: route agents to only the specification documents needed for the current task.

## How to Use
1. Read `docs/handoff/NEXT_TASK.md`.
2. Match task scope to entries below.
3. Open only relevant spec files/sections.
4. Add new specs here immediately when created.

## Entry Format
- `path`: spec file path
- `summary`: what the document defines
- `tags`: routing keywords
- `read-when`: explicit trigger for loading this spec

## Specs
- `path`: `docs/specs/data-sourcing-and-eligibility.md`
- `summary`: authoritative candidate-source and strict eligibility rules for model repositories.
- `tags`: `model-selection`, `eligibility`, `manifest`, `data-sourcing`
- `read-when`: tasks involve selecting model candidates, validating repo eligibility, or deciding exclusions.

- `path`: `docs/specs/extraction-and-normalization.md`
- `summary`: contract for artifact acquisition, OSV raw output handling, and normalized vulnerability schema.
- `tags`: `ingestion`, `osv`, `normalization`, `schema`
- `read-when`: tasks involve fetching dependency artifacts, scanning vulnerabilities, or writing normalized outputs.

- `path`: `docs/specs/graph-semantics-and-metrics.md`
- `summary`: graph node/edge semantics and required baseline metrics for atlas evaluation.
- `tags`: `graph`, `metrics`, `networkx`, `risk-structure`
- `read-when`: tasks involve graph construction, edge rules, deduplication identity, or reporting metrics.

When adding another spec, use this template:

- `path`: `docs/specs/<filename>.md`
- `summary`: <one to two sentence authoritative scope>
- `tags`: `<tag1>`, `<tag2>`, `<tag3>`
- `read-when`: <specific condition>
