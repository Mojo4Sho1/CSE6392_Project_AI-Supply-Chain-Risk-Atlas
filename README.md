# CSE6392_Project_AI_Supply_Chain_Risk_Atlas

# AI Supply Chain Risk Atlas

Graph-based vulnerability mapping of open-source AI model ecosystems.

This project builds a **typed dependency graph** over a small sample of **popular Hugging Face models**, annotates dependency nodes with **known vulnerabilities**, and produces an interpretable “risk atlas” that highlights **where risk concentrates** and **how it propagates** through shared dependencies.

---

## Goals

1. Build a reproducible pipeline to:
   - Select a constrained sample of open-source AI models
   - Extract dependencies (direct + transitive) from their public repos
   - Identify known vulnerabilities affecting those dependencies
   - Construct a typed **Model–Package risk graph**
2. Produce an “atlas-style” set of analyses and visualizations:
   - Rank models by dependency-related vulnerability exposure
   - Identify **shared vulnerable packages** creating cross-model risk
   - Highlight vulnerability “hotspots” in the ecosystem

---

## Scope

### Included
- **10–20 popular Hugging Face models** (sample is intentionally constrained; v1 target is 15)
- Models with:
  - A **public source repository** available
  - **Usable dependency artifacts** (manifests and/or lockfiles)

### Excluded
- Closed-source models
- Repos with insufficient dependency visibility (e.g., no manifests/lockfiles, or artifacts that cannot be scanned)

> Note: Vulnerability data is typically **package + version scoped**. In v1, if a repo does not pin versions, findings are marked as **unknown**.

---

## High-Level Pipeline

1. **Model selection**
   - Use human-curated rows in `data/models.csv` (v1 default)
   - Validate candidate rows against strict eligibility policy
   - Freeze per-model intake and provenance into `manifests/<model_id>/manifest_index.json`

2. **Repo ingestion**
   - Fetch dependency artifacts only (artifact-only mode)
   - Record commit SHA
   - Collect dependency artifacts (e.g., `requirements.txt`, `poetry.lock`, `package.json`, lockfiles)

3. **Dependency + vulnerability extraction**
   - Run **OSV-Scanner** over each selected model's dependency artifact set
   - Store raw scanner outputs
   - Normalize results into a stable schema for graph construction

4. **Graph construction**
   - Build a typed graph:
     - Model nodes
     - Package nodes
     - Typed edges for dependency relationships
   - Annotate package nodes with vulnerability features (severity bucket, fix availability, etc.)

5. **Evaluation + reporting**
   - Compute metrics (dependency footprint, vulnerability exposure, risk structure)
   - Generate ranked views and visuals (“atlas” outputs)

---

## Data Artifacts and Directory Layout

This repo is expected to produce and/or store the following artifacts:

```
data/
  models.csv                   # curated candidate list and v1 authoritative input
manifests/
  <model_id>/manifest_index.json
osv/
  <model_id>/raw.json          # raw OSV-Scanner JSON output
  <model_id>/normalized.json   # normalized schema for graph build
graphs/
  global.graphml               # full atlas graph
  per_model/
    <model_id>.graphml         # optional per-model subgraph
reports/
  summary.json                 # aggregate metrics
  summary.csv                  # tabular metrics / rankings
figures/
  ...                          # plots / atlas visuals
docs/
  specs/
    _INDEX.md                  # spec routing table for selective agent loading
    decision-log.md            # accepted policy defaults and change-control
  handoff/
    CURRENT_STATUS.md          # current project status
    NEXT_TASK.md               # next concrete task batch
    PROJECT_CHECKLIST.md       # end-to-end milestone checklist and gates
paper/
  final_report.tex             # simple LaTeX draft for the final write-up / Overleaf handoff
```

---

## Dataset Input and Freeze Boundary

In the implemented v1 pipeline, `data/models.csv` is the human-curated authoritative input file containing final selected candidates only.

This makes analysis reproducible even if model popularity or repository state changes over time.

The reproducible freeze boundary is the per-model manifest set written to:

- `manifests/<model_id>/manifest_index.json`

v1 policy defaults:
- `data/models.csv` is human-owned input.
- default sample target is 15 models.
- automated model ranking is deferred.
- `dependency_artifact` and `dependency_artifact_url` are optional human-curated hints; the ingestion script uses them as a starting point but may discover additional artifacts.
- Eligibility is determined at runtime and recorded in output artifacts.

For `data/models.csv`, columns are:

| Column | Type | Required | Allowed values / format | Meaning |
|---|---|---|---|---|
| `hf_model_id` | string | yes | non-empty | Hugging Face model ID (e.g., `org/model`) |
| `source_repo_url` | string | yes | public repo URL | Canonical source repository URL |
| `dependency_artifact` | string | no | free text | Human hint: artifact filename/path |
| `dependency_artifact_url` | string | no | URL | Direct URL to artifact in source repo |
| `snapshot_timestamp_utc` | string | yes | `YYYY-MM-DDTHH:MM:SSZ` | Time the popularity metrics were captured |
| `hf_downloads_at_snapshot` | integer | yes | `>= 0` | Downloads value at snapshot time |
| `hf_likes_at_snapshot` | integer | yes | `>= 0` (shorthand like "2.59k" accepted) | Likes value at snapshot time |
| `selection_rationale` | string | no | free text | Why this model was selected |
| `curation_notes` | string | no | free text | Optional operator notes |

### How To Curate `models.csv` Rows (v1)

1. Find top candidate models on Hugging Face using likes/downloads.
2. Keep only models with public source repositories.
3. Verify the source repo has a recognizable dependency artifact (e.g., `requirements.txt`, `pyproject.toml`).
4. Enter one row per final selected candidate with snapshot metrics and artifact hints.
5. Eligibility is computed at runtime; do not add an `eligible` column.

---

## Agent Workflow

This repository is set up for agent-to-agent handoff and selective spec loading:

1. Read `AGENTS.md`
2. Read `docs/handoff/QUICK_REFERENCE.md`
3. Read `docs/handoff/CURRENT_STATUS.md`
4. Read `docs/handoff/NEXT_TASK.md`
5. Read `docs/handoff/TASK_QUEUE.md`
6. Read `docs/handoff/CAMPAIGN_PLAN.md`
7. Read `docs/handoff/PROJECT_CHECKLIST.md`
8. Read `docs/specs/_INDEX.md`
9. Read only relevant spec files for the active task

## Authoritative Contracts

For implementation decisions, use these specs:

- `docs/specs/decision-log.md` (policy defaults)
- `docs/specs/artifact-schemas.md` (artifact schemas + enums)
- `docs/specs/pipeline-execution-contract.md` (CLI/runtime behavior)
- `docs/specs/testing-and-validation.md` (required validation gates)

---

## Environment Setup

Create and activate the shared conda environment:

```bash
conda env create -f environment.yml
conda activate ai-supply-chain-risk-atlas
```

Install OSV-Scanner separately as an external prerequisite on macOS:

```bash
brew install osv-scanner
osv-scanner --version
```

`environment.yml` manages the Python environment only; OSV-Scanner is expected to be available on your shell `PATH`.

## Running the Pipeline

From the repository root:

```bash
make ingest
make scan
make graph
make report
make all
make dashboard
make validate
```

Command notes:

- `make all` executes the full M1-M4 stage chain through reporting and may reuse already-generated stage outputs.
- `make dashboard` launches the local read-only Dash + Plotly showcase against `graphs/global.graphml`, `reports/summary.json`, and `reports/summary.csv`.
- `make validate` runs the Phase 5 local validation bundle: CLI smoke checks, `make all`, `make test`, artifact existence checks, and the unresolved-decision grep from `docs/specs/testing-and-validation.md`.
- Use `make clean` before `make all` only when you intentionally want to regenerate all pipeline outputs from scratch.

## Local Dashboard

The optional showcase layer is a single-page Dash app with a Plotly-based graph explorer.

Launch it from repo root with:

```bash
make dashboard
```

Behavior notes:

- it reads the existing graph/report artifacts once at startup and does not regenerate pipeline outputs
- the explorer is intentionally renderer-separated so a future Cytoscape swap can reuse the same data/view-model logic
- the current v1 renderer is Plotly-only; `dash-cytoscape` is intentionally deferred

---

## Graph Schema

### Node Types

#### 1) `Model`
Represents a Hugging Face model in the selected sample.

Minimum attributes:
- `hf_model_id`
- `source_repo_url`
- `snapshot_timestamp_utc`

#### 2) `Package`
Represents a dependency package used by one or more model repos.

Minimum attributes:
- `ecosystem` (e.g., `PyPI`, `npm`, `Maven`, `Go`, etc.)
- `name`
- `version` (string, or `null`/`unknown` if not resolvable)

> Identity rule (deduplication): a package node is uniquely identified by `(ecosystem, name, version)`.

### Edge Types

#### 1) `uses_package` (Model → Package)
Indicates that a model depends on a package (directly or transitively).

Recommended attributes:
- `dependency_scope`: `direct` | `transitive`
- `depth`: integer depth when derivable (0 = direct)
- `manifest_source`: file path that produced this relation (if known)

#### 2) `depends_on` (Package → Package)
Indicates package-to-package dependency relationships.

Recommended attributes:
- `edge_source`: lockfile vs scanner-derived dependency graph (if available)

> v1 default: `depends_on` is deferred and not required for milestone completion.

---

## Vulnerability Annotation

Vulnerabilities are attached as **node features** on `Package` nodes.

Recommended package vulnerability fields:
- `vuln_status`:
  - `vulnerable` (known version matches an affected range)
  - `not_vulnerable` (known version does not match)
  - `unknown` (version is missing / cannot evaluate precisely)
- `vuln_ids`: list of OSV/CVE/GHSA identifiers
- `num_vulns`: integer count of unique `vuln_ids`
- `max_severity_bucket`: `LOW | MEDIUM | HIGH | CRITICAL | UNKNOWN`
- `fix_available`: boolean (true if OSV indicates a known fix version exists)

### Version Resolution Policy

Because vulnerability matching is package+version scoped:

- If a lockfile pins versions, vulnerability status is **observed** (`vulnerable` / `not_vulnerable`).
- If versions are unpinned, status is **unknown** in v1.

This policy should remain consistent across all models in the dataset.

---

## Evaluation Metrics

### 1) Dependency Footprint
- **Unique packages (global):** count distinct Package nodes
- **Average packages per model:** mean number of package neighbors per Model
  - broken out into direct vs transitive if available

### 2) Vulnerability Exposure
- **Vulnerable direct dependencies:** per-model count of vulnerable packages with `dependency_scope=direct`
- **Vulnerable transitive dependencies:** per-model count with `dependency_scope=transitive`
- **Vulnerabilities per model:**
  - `vulnerable_packages_per_model`
  - `unique_vuln_ids_per_model`

### 3) Risk Structure
- **Most reused vulnerable packages:** rank vulnerable packages by number of distinct models connected
- **Models impacted per vulnerable package:** distribution of model counts per vulnerable package

---

## Milestones

### M1 — Ingestion & eligibility
- Parse and validate `data/models.csv`
- Generate `manifests/<model_id>/manifest_index.json`

### M2 — Dependency + vulnerability extraction
- Run OSV scanning across eligible model artifact sets
- Normalize outputs into `osv/<model_id>/normalized.json`

### M3 — Graph construction & validation
- Build typed graph (`graphs/global.graphml`)
- Validate package deduplication and edge integrity

### M4 — Evaluation, visualization, and reporting
- Compute the required baseline metrics and rankings
- Generate final figures / atlas visuals
- Produce `reports/summary.(json|csv)`

### M5 — Local showcase dashboard
- Launch the single-page Dash + Plotly explorer with `make dashboard`
- Browse overview metrics, the typed graph, and model/package detail panels without mutating pipeline artifacts

---

## Tooling (minimal stack)

- Hugging Face API / metadata
- **OSV-Scanner**
- Python + NetworkX
- Dash + Plotly for the local showcase dashboard

---

## Notes / Non-Goals

- This project focuses on **dependency-driven** exposure, not model behavior, alignment, or dataset safety.
- Findings are limited by:
  - dependency visibility in repos
  - quality of version pinning
  - coverage/precision of public vulnerability databases

---

## License

TBD.
