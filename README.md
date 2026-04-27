# AI Supply Chain Risk Atlas

A reproducible pipeline for analyzing dependency-driven security exposure across open-source AI model ecosystems.

This repository builds a model-centered **risk atlas** over a curated sample of open-source Hugging Face model repositories. Instead of treating each repository as an isolated scan target, the project constructs a typed **model–package graph** that shows where vulnerable packages appear, which models reuse them, and how dependency-driven exposure overlaps across the sample.

The pipeline is intentionally artifact-driven and reproducible. Each stage emits inspectable intermediate outputs so that results can be audited, regenerated, and explored through both static reports and a local dashboard.

---

## Current Status

This repository contains a completed **v1 pipeline** for analyzing dependency-driven software supply chain exposure in a curated sample of open-source Hugging Face model repositories.

Implemented components include:

- curated model intake via `data/models.csv`
- artifact-only dependency ingestion
- OSV-based vulnerability scanning and normalization
- typed model–package graph construction
- aggregate reporting and figure generation
- local read-only dashboard via `make dashboard`

The current workflow is designed to preserve intermediate artifacts at each stage so that results remain reproducible and easy to inspect.

---

## Quickstart

### 1. Create the environment

```bash
conda env create -f environment.yml
conda activate ai-supply-chain-risk-atlas
```

### 2. Install OSV-Scanner

Install OSV-Scanner separately and ensure it is available on your `PATH`.

### 3. Run the full pipeline

```bash
make all
```

### 4. Validate the generated outputs

```bash
make validate
```

### 5. Launch the local dashboard

```bash
make dashboard
```

---

## What This Repository Produces

The repository produces a small set of high-value outputs:

- **Curated model input**
  - `data/models.csv`
- **Per-model manifest and provenance artifacts**
  - generated during ingestion
- **Normalized vulnerability findings**
  - generated during scanning
- **Global model–package graph**
  - generated during graph construction
- **Aggregate reports and figures**
  - generated during reporting
- **Local dashboard**
  - reads the graph and report artifacts at startup

Representative output locations include:

- `graphs/global.graphml`
- `reports/summary.json`
- `reports/summary.csv`
- `figures/`

---

## High-Level Pipeline

The repository is organized as a reproducible four-stage pipeline followed by optional local visualization.

### M1. Ingest
Collect model metadata and dependency artifacts from the selected repositories, record provenance, and evaluate eligibility.

### M2. Scan
Run OSV-Scanner on eligible dependency artifacts and normalize raw findings into a stable schema for downstream processing.

### M3. Graph
Build a typed global graph over model nodes and package nodes.

### M4. Report
Compute aggregate metrics, per-model summaries, rankings, and figure-ready outputs.

### Dashboard
Load the generated graph and report artifacts into a local interactive explorer for inspection and presentation.

---

## Dataset and Selection Policy

The authoritative curated input is:

- `data/models.csv`

The dataset is intentionally constrained so that the analysis remains reproducible and each candidate can be evaluated against the same visibility rules.

### Inclusion criteria

A model repository is eligible only if it satisfies all of the following:

- public source repository available
- dependency artifacts are discoverable
- dependency visibility is sufficient for downstream analysis

### Exclusion criteria

The following are excluded from the curated sample:

- closed-source models
- repositories without usable dependency artifacts
- repositories with insufficient dependency visibility for reproducible analysis

This project does **not** attempt to crawl the full Hugging Face ecosystem automatically. Instead, it uses a curated input file so that the sample remains interpretable and stable across runs.

---

## Graph and Vulnerability Model

### Node types

The atlas graph uses two node types:

- **Model**
  - a selected Hugging Face model repository
- **Package**
  - a deduplicated dependency identified by the tuple `(ecosystem, name, version)`

### Edge types

The validated v1 graph uses the edge type:

- **`uses_package`**
  - directed from `Model -> Package`

For v1, dependency scope is represented as:

- `direct`
- `transitive`

### Vulnerability annotations

Package nodes retain vulnerability-related attributes such as:

- vulnerability status
- severity bucket
- fix availability
- vulnerability identifiers

### Version resolution policy

The project uses a conservative version-resolution policy.

- If a package version is pinned tightly enough to support precise evaluation, the package can be labeled as observed vulnerable or observed not vulnerable.
- If the version is missing, unresolved, or not pinned tightly enough to support precise evaluation, the package is assigned `vuln_status=unknown`.

In other words, **`unknown` belongs to vulnerability evaluation**, not to dependency scope. This distinction is important in the current v1 design.

---

## Dashboard

The repository includes an optional single-page local dashboard that loads the generated graph and report artifacts at startup and exposes the atlas as an interactive graph explorer.

Launch it with:

```bash
make dashboard
```

The dashboard is designed as a **read-only visualization layer** over the generated artifacts. It supports quick inspection of:

- model/package relationships
- visible graph structure
- snapshot metrics
- reuse hotspots
- selected-model dependency neighborhoods

The current implementation uses Plotly and preserves a renderer seam so that future interface refinements can be introduced without rewriting the core data-loading and filtering logic.

---

## Evaluation Outputs

The reporting stage summarizes the atlas through three main output categories.

### Dependency footprint

Examples include:

- unique packages
- average packages per model
- direct vs. transitive package counts

### Vulnerability exposure

Examples include:

- vulnerable direct dependencies
- vulnerable transitive dependencies
- vulnerability counts per model

### Risk structure

Examples include:

- most reused vulnerable packages
- impacted models per vulnerable package
- cross-model structural overlap in exposure

These outputs are intended to make dependency-driven risk easier to inspect and communicate than a flat repository-level scan report.

---

## Reproducibility Notes

This project favors **artifact-only ingestion** over cloning full repositories as the primary evidence boundary.

That design choice has two benefits:

1. it keeps the workflow deterministic and easier to reproduce
2. it makes the analysis boundary clearer by focusing on dependency-relevant artifacts

The project also uses a curated dataset rather than unconstrained crawling so that selection decisions remain understandable and repeatable.

---

## Limitations and Non-Goals

This repository studies **dependency-driven software supply chain exposure**.

It does **not** attempt to measure:

- model behavior risk
- alignment or misuse risk
- dataset quality or safety
- general AI safety properties

The current findings are constrained by:

- dependency visibility in public repositories
- version pinning quality
- public vulnerability database coverage
- scanner precision and normalization limits

These limitations do not invalidate the atlas, but they do define the confidence boundary around the reported findings.

---

## Detailed Docs and Internal Specs

More detailed execution contracts, handoff notes, and internal specifications live under `docs/`.

Use the README as the primary entry point for:

- what the project is
- how to run it
- what artifacts it produces
- how to interpret the outputs

Use `docs/` for lower-level implementation details and internal project documentation.

---

## Repository Link

Project source code:

- <https://github.com/Mojo4Sho1/CSE6392_Project_AI-Supply-Chain-Risk-Atlas>

---

## Suggested Entry Points

If you are new to the repository, start here:

1. `data/models.csv`
2. `Makefile`
3. `graphs/global.graphml`
4. `reports/summary.json`
5. `reports/summary.csv`

If you want to demo or inspect the project interactively, run:

```bash
make dashboard
```

---

## License

Add the project license here once finalized.
