"""Reusable dashboard fixtures for unit and integration tests."""

from __future__ import annotations

from pathlib import Path

from scripts._utils.graph_build import build_global_graph, write_graphml_atomic
from scripts._utils.report_build import (
    build_summary_payload,
    write_summary_csv,
    write_summary_json,
)

SNAPSHOT_TS = "2026-03-24T00:00:00Z"


def package(
    *,
    ecosystem: str = "PyPI",
    name: str,
    version: str | None,
    dependency_scope: str,
    manifest_source: str = "requirements.txt",
    vuln_status: str,
    vuln_ids: list[str] | None = None,
    max_severity_bucket: str = "UNKNOWN",
    fix_available: bool = False,
) -> dict:
    package_vuln_ids = [] if vuln_ids is None else vuln_ids
    return {
        "dependency_scope": dependency_scope,
        "ecosystem": ecosystem,
        "fix_available": fix_available,
        "manifest_source": manifest_source,
        "max_severity_bucket": max_severity_bucket,
        "name": name,
        "num_vulns": len(package_vuln_ids),
        "version": version,
        "vuln_ids": package_vuln_ids,
        "vuln_status": vuln_status,
    }


def normalized_record(*, hf_model_id: str, model_id: str, packages: list[dict]) -> dict:
    return {
        "generated_at_utc": SNAPSHOT_TS,
        "hf_model_id": hf_model_id,
        "model_id": model_id,
        "packages": packages,
        "repo_commit_sha": "abc123",
        "repo_commit_sha_reason": "none",
        "scanner": {
            "name": "osv-scanner",
            "version": "2.3.5",
        },
        "schema_version": "1.0",
        "source_repo_url": f"https://github.com/example/{model_id}",
    }


def write_dashboard_artifacts(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a small, deterministic graph/report artifact trio for tests."""
    graph = build_global_graph(
        normalized_records=[
            normalized_record(
                hf_model_id="example/model-a",
                model_id="example--model-a--11111111",
                packages=[
                    package(
                        name="shared-lib",
                        version="1.0.0",
                        dependency_scope="direct",
                        vuln_status="vulnerable",
                        vuln_ids=["GHSA-demo-1", "GHSA-demo-2"],
                        max_severity_bucket="HIGH",
                        fix_available=True,
                    ),
                    package(
                        name="safe-lib",
                        version="2.0.0",
                        dependency_scope="transitive",
                        vuln_status="not_vulnerable",
                    ),
                ],
            ),
            normalized_record(
                hf_model_id="example/model-b",
                model_id="example--model-b--22222222",
                packages=[
                    package(
                        name="shared-lib",
                        version="1.0.0",
                        dependency_scope="transitive",
                        vuln_status="vulnerable",
                        vuln_ids=["GHSA-demo-1", "GHSA-demo-2"],
                        max_severity_bucket="HIGH",
                        fix_available=True,
                    ),
                    package(
                        name="mystery-lib",
                        version=None,
                        dependency_scope="direct",
                        vuln_status="unknown",
                        vuln_ids=[],
                        max_severity_bucket="UNKNOWN",
                    ),
                ],
            ),
            normalized_record(
                hf_model_id="example/model-c",
                model_id="example--model-c--33333333",
                packages=[],
            ),
        ],
        snapshot_timestamp=SNAPSHOT_TS,
    )

    graph_path = tmp_path / "graphs" / "global.graphml"
    write_graphml_atomic(graph, graph_path)
    summary_payload = build_summary_payload(graph=graph, graph_source=graph_path)
    summary_path = write_summary_json(tmp_path, summary_payload)
    table_path = write_summary_csv(tmp_path, summary_payload["per_model_metrics"])
    return graph_path, summary_path, table_path
