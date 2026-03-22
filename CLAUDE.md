# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AI Supply Chain Risk Atlas — a graph-based vulnerability mapping system for open-source AI model ecosystems. Builds a typed dependency graph over popular Hugging Face models, annotates nodes with known vulnerabilities (via OSV-Scanner), and produces a risk atlas showing where vulnerabilities concentrate and propagate through shared dependencies. Graduate project for CSE 6392.

## Environment Setup

```bash
conda env create -f environment.yml
conda activate ai-supply-chain-risk-atlas
```

Python 3.11. Key dependencies: pandas, networkx, matplotlib, seaborn, requests, huggingface-hub, pytest. External tool required for M2: OSV-Scanner.

## Context-Loading Workflow

Before starting work, read files in this order (per `AGENTS.md`):

1. `AGENTS.md` — operational guidance, automation policy, testing policy
2. `docs/handoff/QUICK_REFERENCE.md` — single-page cheat sheet (CSV schema, enums, CLI contract, file layout)
3. `docs/handoff/CURRENT_STATUS.md` — project state
4. `docs/handoff/NEXT_TASK.md` — source of truth for immediate work
5. `docs/handoff/TASK_QUEUE.md` — prioritized task backlog
6. `docs/handoff/CAMPAIGN_PLAN.md` — phased roadmap (long-horizon context)
7. `docs/specs/_INDEX.md` — spec routing table (read only specs relevant to current task)
8. `docs/specs/decision-log.md` — read before making any policy assumptions

Do **not** load all specs by default. Use `_INDEX.md` tags and `read-when` triggers to select only what's needed. The quick reference covers most common lookups without loading specs.

## Pipeline Architecture (M1–M4)

Four milestone stages, each a standalone script in `scripts/`:

| Milestone | Script | Input | Output |
|-----------|--------|-------|--------|
| M1: Ingestion | `ingest_repo_artifacts.py` | `data/models.csv` | `manifests/<model_id>/manifest_index.json` |
| M2: OSV Scan | `run_osv_scan.py` | Eligible manifests | `osv/<model_id>/normalized.json` |
| M3: Graph | `build_risk_graph.py` | Normalized OSV | `graphs/global.graphml` |
| M4: Reporting | `generate_atlas_reports.py` | Global graph | `reports/summary.json`, `figures/` |

## Key Conventions

**CLI contract** (all pipeline scripts): flags `--input`, `--output-root`, `--snapshot-timestamp`, `--dry-run`, `--log-level`. Exit codes: 0 success, 2 input error, 3 missing dependency, 4 fatal error.

**JSON outputs**: UTF-8, stable key order, 2-space indent, trailing newline. Timestamps: UTC ISO-8601 with `Z` suffix.

**Deterministic ordering**: by `hf_model_id` ascending, then input row number.

**Package identity**: unique on `(ecosystem, name, version)`.

**`model_id` normalization**: deterministic slug from `hf_model_id` with SHA-1 hash suffix for collision resistance. See `docs/specs/artifact-schemas.md`.

**`data/models.csv` is human-owned** — do not auto-generate or overwrite in v1.

## Schemas

All output schemas are defined in `docs/specs/artifact-schemas.md`. Eligibility reason codes are enumerated in `docs/specs/data-sourcing-and-eligibility.md`.

## Handoff Obligations

After completing any task batch, update both:
- `docs/handoff/CURRENT_STATUS.md`
- `docs/handoff/NEXT_TASK.md`

If any spec changes, update `docs/specs/_INDEX.md` in the same batch.

## Testing

Run tests with `pytest` from repo root. Coverage requirements and validation gates are in `docs/specs/testing-and-validation.md`.
