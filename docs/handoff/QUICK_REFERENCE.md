# Quick Reference

Single-page cheat sheet for agents. Intentionally duplicates key info from specs so you can orient without loading 6 files. For authoritative detail, follow the spec pointers.

## CSV Schema (`data/models.csv`)

| Column | Required | Type | Notes |
|--------|----------|------|-------|
| `hf_model_id` | yes | string | e.g., `google-bert/bert-base-uncased` |
| `source_repo_url` | yes | string | GitHub URL to official repo |
| `dependency_artifact` | no | string | Human hint: artifact filename/path (e.g., "requirements.txt (root)") |
| `dependency_artifact_url` | no | string | Direct URL to artifact in source repo |
| `snapshot_timestamp_utc` | yes | timestamp | ISO-8601 with Z suffix |
| `hf_downloads_at_snapshot` | yes | integer | Non-negative |
| `hf_likes_at_snapshot` | yes | integer | Accepts shorthand like "2.59k" in CSV; normalize to int during ingestion |
| `selection_rationale` | no | string | Freeform text: why this model was selected |
| `curation_notes` | no | string | Operator notes |

**Spec:** `docs/specs/data-sourcing-and-eligibility.md`

## `model_id` Normalization (7 steps)

1. Lowercase `hf_model_id`
2. Replace `/` with `--`
3. Replace chars outside `[a-z0-9._-]` with `-`
4. Collapse repeated `-` to single `-`
5. Trim leading/trailing `-`
6. If empty, use `model`
7. Append `--` + first 8 hex of SHA-1(`hf_model_id`)

Result: `<slug>--<hash8>` (e.g., `google-bert--bert-base-uncased--a1b2c3d4`)

**Spec:** `docs/specs/artifact-schemas.md` (normalization section)

## Canonical Enums

### `eligibility_reason_code`
`OK_ELIGIBLE`, `ERR_INPUT_MISSING_REQUIRED_FIELD`, `ERR_INPUT_INVALID_TIMESTAMP`, `ERR_REPO_UNREACHABLE`, `ERR_REPO_FORBIDDEN`, `ERR_REF_RESOLUTION_FAILED`, `ERR_NO_SUPPORTED_ARTIFACTS`, `ERR_ARTIFACT_FETCH_FAILED`, `ERR_ARTIFACT_PARSE_FAILED`, `ERR_MODEL_ARTIFACT_MAPPING_AMBIGUOUS`

### `dependency_scope`
`direct`, `transitive`, `unknown`

### `vuln_status` (v1)
`vulnerable`, `not_vulnerable`, `unknown`

### `severity_bucket`
`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `UNKNOWN`

**Spec:** `docs/specs/artifact-schemas.md` (enums section)

## CLI Contract (all pipeline scripts)

**Flags:** `--input`, `--output-root`, `--snapshot-timestamp`, `--dry-run`, `--log-level`

**Exit codes:**
| Code | Meaning |
|------|---------|
| 0 | Success (including expected ineligibility) |
| 2 | Input contract error (bad CSV, missing fields) |
| 3 | Missing external dependency (e.g., OSV-Scanner) |
| 4 | Fatal runtime error |

**Spec:** `docs/specs/pipeline-execution-contract.md`

## JSON Output Rules

- UTF-8, stable key ordering, 2-space indent, trailing newline
- Timestamps: UTC ISO-8601 with `Z` suffix
- Deterministic ordering: by `hf_model_id` ascending, then input row number
- Package identity: unique on `(ecosystem, name, version)`

## Output File Layout

```
manifests/<model_id>/manifest_index.json   # M1: per-model ingestion output
osv/<model_id>/raw.json                    # M2: raw OSV scanner output
osv/<model_id>/normalized.json             # M2: normalized vulnerability data
graphs/global.graphml                      # M3: typed atlas graph
reports/summary.json                       # M4: metrics and rankings
reports/summary.csv                        # M4: tabular metrics
figures/                                   # M4: visualizations
```

## Recognized Dependency Artifacts

**Python:** `requirements.txt`, `pyproject.toml`, `poetry.lock`, `Pipfile`, `Pipfile.lock`
**JavaScript/Node:** `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`

## Spec Routing (when to read what)

| Need to know about... | Read this spec |
|------------------------|----------------|
| CSV schema, eligibility rules | `data-sourcing-and-eligibility.md` |
| Output schemas, enums, model_id normalization | `artifact-schemas.md` |
| Artifact fetching, OSV normalization | `extraction-and-normalization.md` |
| Graph nodes/edges, metrics | `graph-semantics-and-metrics.md` |
| CLI flags, exit codes, determinism | `pipeline-execution-contract.md` |
| Test fixtures, coverage gates | `testing-and-validation.md` |
| Policy defaults, locked decisions | `decision-log.md` |

## Dashboard Redesign Routing (2026-03-26)

If the active task touches dashboard redesign or UI work, read `docs/dashboard_redesign_plan.md` immediately after the standard handoff files.

Locked redesign decisions:

- implement one redesign stage per batch; do not combine stages
- keep Dash as the app framework
- keep the current Plotly renderer through Stages 0-2
- defer Cytoscape migration to Stage 3
- preserve current analytical semantics unless a stage explicitly changes presentation behavior
- use a graph-first shell: top bar, left sidebar, center graph, right inspector
- keep single-node selection only; do not add compare mode
- hide package labels by default and allow a label toggle later
- use a dark shell with a light graph canvas

Current dashboard code locations:

- `scripts/run_dashboard.py`
- `scripts/_utils/dashboard_data.py`
- `scripts/_utils/dashboard_controller.py`
- `scripts/_utils/dashboard_layout.py`
- `scripts/_utils/dashboard_view.py`
- `scripts/_utils/dashboard_render_plotly.py`
- `scripts/_utils/dashboard_app.py`
- `scripts/_utils/dashboard_theme.py`
- `assets/dashboard.css`
- `assets/branding/README.md`
- `docs/dashboard_architecture_note.md`

Full routing table with tags: `docs/specs/_INDEX.md`
