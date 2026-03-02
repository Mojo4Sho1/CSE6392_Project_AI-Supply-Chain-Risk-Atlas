# Project Checklist

**Last updated:** 2026-03-02  
**Owner:** Joe + Codex

## Purpose

Provide a decision-complete, end-to-end execution checklist for milestones M1-M4.  
`docs/handoff/NEXT_TASK.md` remains the source of truth for the immediate batch.  
This file is the long-horizon control document for zero-context agents.

## Locked v1 Defaults

- `data/models.csv` rows are human-owned and human-approved.
- Candidate generation policy is manual curation in `data/models.csv`.
- Default target sample size is 15 models (within project range 10-20).
- Unpinned dependencies must map to `vuln_status=unknown`.
- Ambiguous repository refs resolve to default-branch `HEAD` with provenance.
- Required v1 graph edge type is `uses_package`; `depends_on` is deferred.
- Composite risk score is out of scope for v1; baseline metrics only.

## Global Preconditions

- Environment:
  - `conda env create -f environment.yml`
  - `conda activate ai-supply-chain-risk-atlas`
- Input source:
  - `data/models.csv` is authoritative for v1 candidate intake.
- Determinism:
  - iterate candidates in stable sorted order,
  - serialize JSON with stable key ordering,
  - write outputs atomically,
  - keep all timestamps in UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- Contracts:
  - schema and enum contracts in `docs/specs/artifact-schemas.md`,
  - CLI and runtime contracts in `docs/specs/pipeline-execution-contract.md`.

## Milestone Gates

### M1: Ingestion and Eligibility Baseline

**Objective**  
Build deterministic artifact-ingestion outputs from `data/models.csv` under strict eligibility policy.

**Required inputs**
- `data/models.csv`
- `docs/specs/data-sourcing-and-eligibility.md`
- `docs/specs/extraction-and-normalization.md`
- `docs/specs/artifact-schemas.md`
- `docs/specs/pipeline-execution-contract.md`

**Required outputs**
- `manifests/<model_id>/manifest_index.json` for every candidate row
- Optional run-level logs for diagnostics

**Checklist**
- [ ] Implement ingestion script contract.
- [ ] Enforce required CSV fields and strict eligibility checks.
- [ ] Emit canonical eligibility `reason_code` values.
- [ ] Capture provenance (`source_repo_url`, resolved ref, commit SHA or unknown reason, evaluation timestamp).
- [ ] Guarantee deterministic output formatting and ordering.

**Acceptance gate**
- [ ] At least one eligible and one ineligible path represented in outputs (fixtures or real rows).
- [ ] All manifest files validate against the v1 manifest schema.
- [ ] No undocumented reason codes are emitted.

### M2: OSV Scan and Normalization

**Objective**  
Generate raw OSV results and normalized vulnerability data for all eligible models.

**Required inputs**
- Eligible `manifest_index.json` outputs from M1
- OSV scanner available in runtime environment
- `docs/specs/extraction-and-normalization.md`
- `docs/specs/artifact-schemas.md`

**Required outputs**
- `osv/<model_id>/raw.json`
- `osv/<model_id>/normalized.json`

**Checklist**
- [ ] Scan only eligible candidates from M1 outputs.
- [ ] Persist raw scanner output unchanged.
- [ ] Normalize to schema version `1.0`.
- [ ] Set `vuln_status=unknown` for unpinned versions.
- [ ] Keep package identity invariant `(ecosystem, name, version)`.

**Acceptance gate**
- [ ] Every raw output has a paired normalized output.
- [ ] Normalized files validate against schema and enum contracts.
- [ ] Scanner name/version and provenance are present in each normalized file.

### M3: Graph Build and Validation

**Objective**  
Construct global typed atlas graph and validate semantic correctness.

**Required inputs**
- `osv/<model_id>/normalized.json` for scanned models
- `docs/specs/graph-semantics-and-metrics.md`
- `docs/specs/artifact-schemas.md`

**Required outputs**
- `graphs/global.graphml`
- Optional: `graphs/per_model/<model_id>.graphml`

**Checklist**
- [ ] Build `Model` and `Package` nodes with required attributes.
- [ ] Build `uses_package` edges with required attributes.
- [ ] Deduplicate packages strictly by `(ecosystem, name, version)`.
- [ ] Enforce graph integrity checks (edge endpoints exist, required attrs present).

**Acceptance gate**
- [ ] Global graph loads without schema/typing errors.
- [ ] Package deduplication and per-model counts match normalized inputs.
- [ ] Deferred `depends_on` edges are not required for v1 completion.

### M4: Reporting and Atlas Outputs

**Objective**  
Produce baseline metrics/rankings and final report artifacts from the graph.

**Required inputs**
- `graphs/global.graphml`
- `docs/specs/graph-semantics-and-metrics.md`
- `docs/specs/artifact-schemas.md`

**Required outputs**
- `reports/summary.json`
- `reports/summary.csv`
- `figures/` visual outputs

**Checklist**
- [ ] Compute baseline dependency, vulnerability, and risk-structure metrics.
- [ ] Emit per-model and aggregate metrics with stable ordering.
- [ ] Generate reproducible figures from the same graph input.

**Acceptance gate**
- [ ] Report outputs validate against schema contracts.
- [ ] Rankings are reproducible for identical inputs.
- [ ] Composite risk score is absent unless the decision log is explicitly revised.

## Cross-Phase Verification Suite

- Routing test:
  - a new agent using required read order can identify exact next steps without ambiguity.
- Contract test:
  - two independent implementations produce schema-equivalent `manifest_index.json` and identical reason-code usage.
- Determinism test:
  - repeated runs with unchanged inputs produce byte-stable sorted outputs except for allowed timestamp fields.
- Negative-path test:
  - unreachable repo, missing artifacts, and parse failure map to distinct reason codes.
- Cross-document consistency test:
  - README, specs, and handoff files express one ingestion policy and one v1 graph edge policy.
- Handoff continuity test:
  - `CURRENT_STATUS.md` and `NEXT_TASK.md` can be updated after each phase without inventing missing policy.

## Handoff Obligations Per Batch

- Update `docs/handoff/CURRENT_STATUS.md` with:
  - concrete completed work,
  - checks run and outcomes,
  - remaining blockers.
- Update `docs/handoff/NEXT_TASK.md` with:
  - one executable next batch,
  - explicit in-scope/out-of-scope,
  - acceptance criteria and verification steps.
- If specs changed:
  - update `docs/specs/_INDEX.md` in the same commit.

## Change Control

- If implementation needs behavior not covered by current specs, add/update spec first.
- If changing locked defaults, update:
  - `docs/specs/decision-log.md`,
  - impacted specs,
  - README statements that reference the changed policy.
