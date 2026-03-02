# Decision Log Spec

## Purpose
Record resolved project policy defaults that were previously open decisions, plus change-control expectations.

**Last updated:** 2026-03-02

## Decision Entries

### DEC-001: Candidate source policy (v1)

- Status: Accepted
- Effective date: 2026-03-02
- Decision:
  - Use manual curated `data/models.csv` as authoritative candidate source in v1.
  - Automated Hugging Face ranking is deferred.
- Rationale:
  - Keeps early iterations deterministic and human-auditable.
- Impact:
  - agents validate and consume rows; they do not auto-populate `data/models.csv`.

### DEC-002: Target sample size (v1)

- Status: Accepted
- Effective date: 2026-03-02
- Decision:
  - Default sample size target is 15 models.
- Rationale:
  - Balances project scope with enough diversity for shared-dependency analysis.
- Impact:
  - checklists and acceptance gates use 15 as default unless explicitly overridden.

### DEC-003: Unpinned vulnerability policy (v1)

- Status: Accepted
- Effective date: 2026-03-02
- Decision:
  - For unpinned dependencies, set `vuln_status=unknown`.
  - Do not use `potentially_vulnerable` in v1 outputs.
- Rationale:
  - avoids over-asserting exposure without package-version evidence.
- Impact:
  - normalization and metric logic must treat unknown as a separate state.

### DEC-004: Repo ref resolution fallback (v1)

- Status: Accepted
- Effective date: 2026-03-02
- Decision:
  - If requested ref is absent/ambiguous, resolve to default-branch `HEAD`.
  - Always record resolution strategy and provenance in manifest output.
- Rationale:
  - provides deterministic fallback while keeping traceability.
- Impact:
  - ingestion outputs must include `requested_ref`, `resolved_ref`, and SHA availability reason.

### DEC-005: Graph edge requirements (v1)

- Status: Accepted
- Effective date: 2026-03-02
- Decision:
  - `uses_package` edges are required in v1.
  - `depends_on` edges are explicitly deferred.
- Rationale:
  - ensures M3 can complete without uncertain transitive edge provenance.
- Impact:
  - no v1 completion criteria may require `depends_on`.

### DEC-006: Composite risk score (v1)

- Status: Accepted
- Effective date: 2026-03-02
- Decision:
  - Composite risk score is out of scope in v1.
- Rationale:
  - baseline metrics must be validated before introducing weighted composite formulas.
- Impact:
  - reports focus on transparent baseline metrics and rankings only.

### DEC-007: Ingestion artifact strategy (v1)

- Status: Accepted
- Effective date: 2026-03-02
- Decision:
  - Default automated ingestion strategy is artifact-only acquisition.
  - Full repository clone is not part of v1 contract execution.
- Rationale:
  - minimizes runtime/storage overhead and reduces nondeterministic repo-side effects.
- Impact:
  - README and specs must describe one artifact flow for v1.

## Change-Control Rules

- To revise any accepted decision:
  1. add a new decision entry referencing superseded decision ID(s),
  2. update impacted specs and README in the same change,
  3. update handoff files if the active task is affected.
- Silent policy drift is not allowed.

## Related Specs

- `docs/specs/data-sourcing-and-eligibility.md`
- `docs/specs/extraction-and-normalization.md`
- `docs/specs/graph-semantics-and-metrics.md`
- `docs/specs/artifact-schemas.md`
- `docs/specs/pipeline-execution-contract.md`
