"""Unit tests for M4 report building helpers."""

from scripts._utils.graph_build import build_global_graph
from scripts._utils.report_build import build_summary_payload


def _package(
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


def _normalized_record(*, hf_model_id: str, model_id: str, packages: list[dict]) -> dict:
    return {
        "generated_at_utc": "2026-03-24T00:00:00Z",
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


class TestBuildSummaryPayload:
    def test_computes_required_metrics_and_deterministic_ordering(self):
        graph = build_global_graph(
            normalized_records=[
                _normalized_record(
                    hf_model_id="z/model",
                    model_id="z--model--33333333",
                    packages=[
                        _package(
                            name="shared-lib",
                            version=None,
                            dependency_scope="direct",
                            vuln_status="vulnerable",
                            vuln_ids=["GHSA-null"],
                            max_severity_bucket="HIGH",
                        ),
                        _package(
                            name="solo-lib",
                            version="1.0.0",
                            dependency_scope="transitive",
                            vuln_status="vulnerable",
                            vuln_ids=["GHSA-solo"],
                            max_severity_bucket="MEDIUM",
                        ),
                    ],
                ),
                _normalized_record(
                    hf_model_id="a/model",
                    model_id="a--model--11111111",
                    packages=[
                        _package(
                            name="shared-lib",
                            version="1.0.0",
                            dependency_scope="direct",
                            vuln_status="vulnerable",
                            vuln_ids=["GHSA-versioned"],
                            max_severity_bucket="CRITICAL",
                        ),
                        _package(
                            name="shared-lib",
                            version=None,
                            dependency_scope="transitive",
                            vuln_status="vulnerable",
                            vuln_ids=["GHSA-null"],
                            max_severity_bucket="HIGH",
                        ),
                    ],
                ),
                _normalized_record(
                    hf_model_id="b/model",
                    model_id="b--model--22222222",
                    packages=[
                        _package(
                            name="shared-lib",
                            version="1.0.0",
                            dependency_scope="transitive",
                            vuln_status="vulnerable",
                            vuln_ids=["GHSA-versioned"],
                            max_severity_bucket="CRITICAL",
                        ),
                        _package(
                            name="safe-lib",
                            version="2.0.0",
                            dependency_scope="direct",
                            vuln_status="not_vulnerable",
                        ),
                    ],
                ),
            ],
            snapshot_timestamp="2026-03-24T00:00:00Z",
        )

        summary = build_summary_payload(graph=graph, graph_source="graphs/global.graphml")

        assert summary["schema_version"] == "1.0"
        assert summary["graph_source"] == "graphs/global.graphml"
        assert summary["snapshot_timestamp_utc"] == "2026-03-24T00:00:00Z"
        assert summary["global_metrics"]["unique_package_count"] == 4
        assert summary["global_metrics"]["average_packages_per_model"] == 2.0
        assert summary["global_metrics"]["average_direct_packages_per_model"] == 1.0
        assert summary["global_metrics"]["average_transitive_packages_per_model"] == 1.0

        assert [row["hf_model_id"] for row in summary["per_model_metrics"]] == [
            "a/model",
            "b/model",
            "z/model",
        ]
        assert summary["per_model_metrics"][0] == {
            "hf_model_id": "a/model",
            "model_id": "a--model--11111111",
            "unique_vuln_ids_per_model": 2,
            "vulnerable_direct_dependencies": 1,
            "vulnerable_packages_per_model": 2,
            "vulnerable_transitive_dependencies": 1,
        }
        assert summary["per_model_metrics"][1] == {
            "hf_model_id": "b/model",
            "model_id": "b--model--22222222",
            "unique_vuln_ids_per_model": 1,
            "vulnerable_direct_dependencies": 0,
            "vulnerable_packages_per_model": 1,
            "vulnerable_transitive_dependencies": 1,
        }
        assert summary["per_model_metrics"][2] == {
            "hf_model_id": "z/model",
            "model_id": "z--model--33333333",
            "unique_vuln_ids_per_model": 2,
            "vulnerable_direct_dependencies": 1,
            "vulnerable_packages_per_model": 2,
            "vulnerable_transitive_dependencies": 1,
        }

        assert summary["reused_vulnerable_packages"] == [
            {
                "ecosystem": "PyPI",
                "impacted_model_count": 2,
                "name": "shared-lib",
                "version": None,
                "vuln_ids": ["GHSA-null"],
            },
            {
                "ecosystem": "PyPI",
                "impacted_model_count": 2,
                "name": "shared-lib",
                "version": "1.0.0",
                "vuln_ids": ["GHSA-versioned"],
            },
            {
                "ecosystem": "PyPI",
                "impacted_model_count": 1,
                "name": "solo-lib",
                "version": "1.0.0",
                "vuln_ids": ["GHSA-solo"],
            },
        ]
