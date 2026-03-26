# Dashboard Showcase Spec

## Purpose

Define the v1 local showcase dashboard for the AI Supply Chain Risk Atlas. This dashboard is a read-only presentation layer over the existing graph and report artifacts and is intended for local demo/class use rather than deployment.

**Last updated:** 2026-03-26

## Status and scope

- Delivery target: local-only v1 dashboard
- Framework: Dash + Plotly
- Layout model: single-page app with overview row, filter rail, graph explorer, and detail panel
- Role in project: optional showcase layer after M4, not a required milestone pipeline output
- Data policy: read-only consumer of pipeline artifacts; must not recompute or mutate M1-M4 outputs
- Renderer policy: keep a renderer seam so a future Cytoscape renderer can reuse the same data/view-model layer

## Inputs

Required runtime inputs:

- `graphs/global.graphml`
- `reports/summary.json`
- `reports/summary.csv`

Input handling rules:

- load all inputs at app startup
- fail fast with a clear error if any required input is missing or malformed
- do not trigger ingestion, scanning, graph rebuild, or report regeneration from the dashboard

## Local runtime contract

Primary entrypoint:

- `python scripts/run_dashboard.py --graph graphs/global.graphml --summary reports/summary.json --table reports/summary.csv --host 127.0.0.1 --port 8050`

Defaults:

- `--graph graphs/global.graphml`
- `--summary reports/summary.json`
- `--table reports/summary.csv`
- `--host 127.0.0.1`
- `--port 8050`

Operational rules:

- bind only to the configured local host in v1
- startup should load artifacts once and keep an in-memory app state for interaction
- no authentication, multi-user state, or deployment configuration is required in v1
- use a deterministic seeded static layout for the initial Plotly graph positioning

## Required app surfaces

The v1 dashboard is a single-page app. These surfaces may appear as sections within that page rather than separate routes.

### 1) Overview page

Must show:

- headline counts derived from report/graph artifacts
- unique package count
- average packages per model
- average direct packages per model
- average transitive packages per model
- top reused vulnerable packages

### 2) Graph explorer

Must show:

- an interactive graph-oriented view of the atlas
- support for narrowing the visible node/edge set through filters
- a selection model that can drive a details panel

### 3) Model detail view

Must show, for a selected model:

- `hf_model_id`
- `model_id`
- dependency counts split by direct/transitive when available
- vulnerable direct dependency count
- vulnerable transitive dependency count
- unique vulnerability count

### 4) Package detail view

Must show, for a selected package:

- `ecosystem`
- `name`
- `version`
- `vuln_status`
- `num_vulns`
- `max_severity_bucket`
- `fix_available`
- impacted model count
- associated vulnerability IDs

## Required interactions

The v1 dashboard must support:

- search by `hf_model_id`
- search by `model_id`
- search by package name
- filter by node type
- filter by `dependency_scope`
- filter by `vuln_status`
- filter by severity bucket
- click/select behavior that updates a side-panel detail view

Interaction defaults:

- all filters default to “show all”
- graph explorer selections are read-only and do not persist beyond the local session
- when multiple filters are active, results are intersected deterministically

## Data interpretation rules

- treat `graphs/global.graphml` as the source of truth for node/edge relationships
- treat `reports/summary.json` and `reports/summary.csv` as the source of truth for precomputed M4 metrics/rankings
- parse package vulnerability IDs from `vuln_ids_json` on package nodes because GraphML stores scalar attributes only
- keep dashboard internals split into:
  - a data layer that loads and normalizes artifacts
  - a pure view-model layer for filtering/search/detail logic
  - a renderer layer that turns the visible graph payload into Plotly traces
- preserve the M3 node typing contract:
  - `node_type=Model`
  - `node_type=Package`
- preserve the M3 edge typing contract:
  - `edge_type=uses_package`

## Non-goals

- hosted deployment
- write-back workflows
- live pipeline execution from the dashboard
- editing graph data
- adding new graph edge types
- replacing the required M4 report artifacts
- adding `dash-cytoscape` in the initial v1 implementation

## Testing and validation expectations

Implementation must include:

- unit tests for graph/report loading and transformation into dashboard-ready structures
- callback/state smoke tests for search, filters, and detail-panel selection
- startup test against fixture graph/report artifacts
- at least one test proving the view-model logic runs without importing Plotly
- at least one renderer test proving the Plotly renderer consumes the canonical visible-graph payload without mutating it
- `python scripts/run_dashboard.py --help` exits 0
- `make dashboard` launches with the documented defaults

## Documentation requirements

When the dashboard is implemented:

- add a `make dashboard` target
- document local launch instructions
- keep the dashboard documented as a showcase/demo layer, not as a required milestone output
- preserve a clean seam so a future `dashboard_render_cytoscape.py` can be added without rewriting the artifact-loading or filter/search logic
