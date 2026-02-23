# Graph Semantics and Metrics Spec

## Purpose
Define authoritative graph structure, node/edge semantics, and baseline evaluation metrics for the risk atlas.

## Graph Types
- Primary graph: global typed graph at `graphs/global.graphml`.
- Optional outputs: per-model subgraphs at `graphs/per_model/<model_id>.graphml`.

## Node Semantics

### Model Node
Required attributes:
- `hf_model_id`
- `source_repo_url`
- `snapshot_timestamp`

### Package Node
Required attributes:
- `ecosystem`
- `name`
- `version`
- `vuln_status`
- `num_vulns`
- `max_severity_bucket`
- `fix_available`

Identity invariant:
- Deduplicate package nodes by `(ecosystem, name, version)`.

## Edge Semantics

### Required in v1
- `uses_package` (Model -> Package)
  - attributes: `dependency_scope`, `depth`, `manifest_source`

### Optional / deferred
- `depends_on` (Package -> Package)
  - include only when dependency relationship is observed with sufficient provenance.

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

## Open Decisions
- `OPEN_DECISION`: v1 requirement level for `depends_on` edges (required now vs phase-gated later).
- `OPEN_DECISION`: whether to introduce a composite risk score; if adopted, formula and calibration must be documented and justified.
