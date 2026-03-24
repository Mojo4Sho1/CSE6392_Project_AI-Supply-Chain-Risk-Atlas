# Graph Semantics and Metrics Spec

## Purpose
Define authoritative graph structure, node/edge semantics, and baseline evaluation metrics for the risk atlas.

**Last updated:** 2026-03-24

Report schema details are defined in `docs/specs/artifact-schemas.md`.

## Graph Types
- Primary graph: global typed graph at `graphs/global.graphml`.
- Optional outputs: per-model subgraphs at `graphs/per_model/<model_id>.graphml`.

## Node Semantics

### Model Node
Required attributes:
- `node_type` (`Model`)
- `model_id`
- `hf_model_id`
- `source_repo_url`
- `snapshot_timestamp_utc`

### Package Node
Required attributes:
- `node_type` (`Package`)
- `ecosystem`
- `name`
- `version`
- `vuln_status`
- `vuln_ids_json` (JSON-encoded sorted array string; GraphML-safe encoding of package vulnerability IDs)
- `num_vulns`
- `max_severity_bucket`
- `fix_available`

Identity invariant:
- Deduplicate package nodes by `(ecosystem, name, version)`.

Duplicate-package merge rule (when the same package key appears in multiple normalized inputs):
- union vulnerability IDs, then recalculate `num_vulns`,
- keep the highest observed `max_severity_bucket`,
- set `fix_available=true` if any contributing record has a fix available,
- resolve `vuln_status` conservatively with precedence `vulnerable > unknown > not_vulnerable`.

## Edge Semantics

### Required in v1
- `uses_package` (Model -> Package)
  - attributes: `edge_type` (`uses_package`), `dependency_scope`, `depth`, `manifest_source`
  - deterministic depth rule for v1:
    - `direct` -> `0`
    - `transitive` -> `1`
    - `unknown` -> `-1`

### Optional / deferred
- `depends_on` (Package -> Package)
  - deferred for v1,
  - include only in future versions when dependency relationship is observed with sufficient provenance.

## Baseline Metrics (required)

### Dependency footprint
- Unique package count (global)
- Packages per model (mean; split by direct/transitive when available)

### Vulnerability exposure
- Vulnerable direct dependencies per model
- Vulnerable transitive dependencies per model
- Unique vulnerability IDs per model

### Risk structure
- Most reused vulnerable packages across models
- Distribution of impacted-model counts per vulnerable package

## Resolved Defaults for v1

- `depends_on` edges are deferred and not required for v1 completion.
- Composite risk score is out of scope; baseline metrics are required.

Decision authority: `docs/specs/decision-log.md`.
