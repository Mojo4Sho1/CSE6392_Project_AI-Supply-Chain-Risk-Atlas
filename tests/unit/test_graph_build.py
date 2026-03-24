"""Unit tests for M3 graph construction helpers."""

import json

import pytest

from scripts._utils.graph_build import (
    GraphContractError,
    build_global_graph,
    make_model_node_id,
    validate_graph,
)


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


class TestBuildGlobalGraph:
    def test_deduplicates_shared_package_nodes_and_keeps_model_edges(self):
        normalized_records = [
            _normalized_record(
                hf_model_id="example/model-a",
                model_id="example--model-a--11111111",
                packages=[
                    _package(
                        name="tqdm",
                        version="4.67.3",
                        dependency_scope="direct",
                        vuln_status="not_vulnerable",
                    )
                ],
            ),
            _normalized_record(
                hf_model_id="example/model-b",
                model_id="example--model-b--22222222",
                packages=[
                    _package(
                        name="tqdm",
                        version="4.67.3",
                        dependency_scope="transitive",
                        manifest_source="poetry.lock",
                        vuln_status="unknown",
                    )
                ],
            ),
        ]

        graph = build_global_graph(
            normalized_records=normalized_records,
            snapshot_timestamp="2026-03-24T00:00:00Z",
        )

        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 2

        package_nodes = [
            (node_id, attrs)
            for node_id, attrs in graph.nodes(data=True)
            if attrs["node_type"] == "Package"
        ]
        assert len(package_nodes) == 1

        package_node_id, package_attrs = package_nodes[0]
        assert package_attrs["name"] == "tqdm"
        assert package_attrs["vuln_status"] == "unknown"
        assert json.loads(package_attrs["vuln_ids_json"]) == []

        edge_depths = {
            (
                graph.nodes[source]["model_id"],
                attrs["dependency_scope"],
            ): attrs["depth"]
            for source, target, attrs in graph.edges(data=True)
            if target == package_node_id
        }
        assert edge_depths[("example--model-a--11111111", "direct")] == 0
        assert edge_depths[("example--model-b--22222222", "transitive")] == 1

    def test_merges_vulnerability_annotations_conservatively(self):
        normalized_records = [
            _normalized_record(
                hf_model_id="example/model-a",
                model_id="example--model-a--11111111",
                packages=[
                    _package(
                        name="transformers",
                        version="4.35.0",
                        dependency_scope="direct",
                        vuln_status="vulnerable",
                        vuln_ids=["GHSA-a", "GHSA-b"],
                        max_severity_bucket="HIGH",
                        fix_available=True,
                    )
                ],
            ),
            _normalized_record(
                hf_model_id="example/model-b",
                model_id="example--model-b--22222222",
                packages=[
                    _package(
                        name="transformers",
                        version="4.35.0",
                        dependency_scope="direct",
                        vuln_status="unknown",
                        vuln_ids=["GHSA-b", "GHSA-c"],
                        max_severity_bucket="CRITICAL",
                        fix_available=False,
                    )
                ],
            ),
        ]

        graph = build_global_graph(
            normalized_records=normalized_records,
            snapshot_timestamp="2026-03-24T00:00:00Z",
        )

        package_attrs = next(
            attrs
            for _, attrs in graph.nodes(data=True)
            if attrs["node_type"] == "Package" and attrs["name"] == "transformers"
        )
        assert package_attrs["vuln_status"] == "vulnerable"
        assert package_attrs["fix_available"] is True
        assert package_attrs["max_severity_bucket"] == "CRITICAL"
        assert package_attrs["num_vulns"] == 3
        assert json.loads(package_attrs["vuln_ids_json"]) == ["GHSA-a", "GHSA-b", "GHSA-c"]

    def test_validate_graph_rejects_invalid_depth_mapping(self):
        graph = build_global_graph(
            normalized_records=[
                _normalized_record(
                    hf_model_id="example/model-a",
                    model_id="example--model-a--11111111",
                    packages=[
                        _package(
                            name="flask",
                            version="1.0.0",
                            dependency_scope="direct",
                            vuln_status="not_vulnerable",
                        )
                    ],
                )
            ],
            snapshot_timestamp="2026-03-24T00:00:00Z",
        )

        model_node_id = make_model_node_id("example--model-a--11111111")
        _, package_node_id = next(iter(graph.edges()))
        graph[model_node_id][package_node_id]["depth"] = 7

        with pytest.raises(GraphContractError, match="expected 0"):
            validate_graph(graph)
