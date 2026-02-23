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
- **10–20 popular Hugging Face models** (sample is intentionally constrained)
- Models with:
  - A **public source repository** available
  - **Usable dependency artifacts** (manifests and/or lockfiles)

### Excluded
- Closed-source models
- Repos with insufficient dependency visibility (e.g., no manifests/lockfiles, or artifacts that cannot be scanned)

> Note: Vulnerability data is typically **package + version scoped**. If a repo does not pin versions, some findings may be marked as **unknown** or **potential** exposure depending on the policy described below.

---

## High-Level Pipeline

1. **Model selection**
   - Query Hugging Face metadata
   - Identify top-liked models
   - Filter to those with public repos and scannable dependency artifacts
   - Freeze the dataset into a snapshot manifest

2. **Repo ingestion**
   - Clone each selected repo
   - Record commit SHA
   - Collect dependency artifacts (e.g., `requirements.txt`, `poetry.lock`, `package.json`, lockfiles)

3. **Dependency + vulnerability extraction**
   - Run **OSV-Scanner** over each repo / dependency file set
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
  models.csv                   # curated candidate list (early-phase source of truth)
  models.json                  # frozen dataset manifest (HF models + repo links)
repos/
  <model_id>/                  # cloned repos (checked out at recorded commit)
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
  handoff/
    CURRENT_STATUS.md          # current project status
    NEXT_TASK.md               # next concrete task batch
```

---

## Dataset Manifest

The dataset is frozen into a single file:

- `data/models.json`

Early project phases may begin with a curated CSV:

- `data/models.csv`

Each entry SHOULD include:
- `hf_model_id`
- `likes_at_snapshot` (and optionally downloads)
- `snapshot_timestamp`
- `source_repo_url`
- `repo_commit_sha` (filled after ingestion)
- `dependency_artifacts_found` (filled after ingestion)

This makes the analysis reproducible even if model popularity or repos change over time.

For `data/models.csv`, required columns are:
- `hf_model_id`
- `source_repo_url`
- `selection_rationale`
- `selection_source`
- `snapshot_timestamp`
- `eligible`

---

## Agent Workflow

This repository is set up for agent-to-agent handoff and selective spec loading:

1. Read `AGENTS.md`
2. Read `docs/handoff/CURRENT_STATUS.md`
3. Read `docs/handoff/NEXT_TASK.md`
4. Read `docs/specs/_INDEX.md`
5. Read only relevant spec files for the active task

---

## Environment Setup

Create and activate the shared conda environment:

```bash
conda env create -f environment.yml
conda activate ai-supply-chain-risk-atlas
```

---

## Graph Schema

### Node Types

#### 1) `Model`
Represents a Hugging Face model in the selected sample.

Minimum attributes:
- `hf_model_id`
- `source_repo_url`
- `snapshot_timestamp`

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

---

## Vulnerability Annotation

Vulnerabilities are attached as **node features** on `Package` nodes.

Recommended package vulnerability fields:
- `vuln_status`:
  - `vulnerable` (known version matches an affected range)
  - `not_vulnerable` (known version does not match)
  - `unknown` (version is missing / cannot evaluate precisely)
  - `potentially_vulnerable` (optional label if using “unpinned = possible exposure” policy)
- `vuln_ids`: list of OSV/CVE/GHSA identifiers
- `num_vulns`: integer count of unique `vuln_ids`
- `max_severity_bucket`: `LOW | MEDIUM | HIGH | CRITICAL | UNKNOWN`
- `fix_available`: boolean (true if OSV indicates a known fix version exists)

### Version Resolution Policy

Because vulnerability matching is package+version scoped:

- If a lockfile pins versions, vulnerability status is **observed** (`vulnerable` / `not_vulnerable`).
- If versions are unpinned, status may be **unknown** (default) unless explicitly treated as **potential exposure**.

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

### M1 — Project scoping & model selection
- Finalize 10–20 models with public repos and scannable dependency artifacts
- Generate `data/models.json` with snapshot metadata

### M2 — Dependency + vulnerability extraction
- Run OSV scanning across all selected repos
- Normalize outputs into a stable schema (`osv/<model_id>/normalized.json`)

### M3 — Graph construction & validation
- Build typed graph (`graphs/global.graphml`)
- Validate:
  - consistent deduplication of packages
  - all edges reference existing nodes
  - per-model package counts align with normalized extraction outputs

### M4 — Evaluation, visualization, and reporting
- Compute all metrics and rankings
- Generate final figures / atlas visuals
- Produce `reports/summary.(json|csv)`

---

## Tooling (minimal stack)

- Hugging Face API / metadata
- **OSV-Scanner**
- Python + NetworkX (+ plotting library)

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
