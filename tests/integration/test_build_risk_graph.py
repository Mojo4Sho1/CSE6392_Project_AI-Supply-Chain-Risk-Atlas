"""Integration tests for build_risk_graph.py."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import networkx as nx

REPO_ROOT = Path(__file__).parent.parent.parent
SCRIPT = str(REPO_ROOT / "scripts" / "build_risk_graph.py")
SNAPSHOT_TS = "2026-03-24T00:00:00Z"


def _write_normalized(
    osv_root: Path,
    *,
    hf_model_id: str,
    model_id: str,
    packages: list[dict],
) -> Path:
    model_dir = osv_root / model_id
    model_dir.mkdir(parents=True, exist_ok=True)
    path = model_dir / "normalized.json"
    payload = {
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
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class TestBuildRiskGraphCli:
    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, SCRIPT, "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        assert "--input" in result.stdout
        assert "--output-root" in result.stdout
        assert "--snapshot-timestamp" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--log-level" in result.stdout


class TestBuildRiskGraphIntegration:
    def test_builds_graphml_with_deduplicated_packages_and_zero_package_model(self, tmp_path):
        from scripts.build_risk_graph import run

        osv_root = tmp_path / "osv"
        _write_normalized(
            osv_root,
            hf_model_id="example/model-a",
            model_id="example--model-a--11111111",
            packages=[
                {
                    "dependency_scope": "direct",
                    "ecosystem": "PyPI",
                    "fix_available": False,
                    "manifest_source": "requirements.txt",
                    "max_severity_bucket": "UNKNOWN",
                    "name": "flask",
                    "num_vulns": 0,
                    "version": "1.0.0",
                    "vuln_ids": [],
                    "vuln_status": "not_vulnerable",
                },
                {
                    "dependency_scope": "transitive",
                    "ecosystem": "PyPI",
                    "fix_available": True,
                    "manifest_source": "requirements.txt",
                    "max_severity_bucket": "HIGH",
                    "name": "shared-lib",
                    "num_vulns": 1,
                    "version": "2.0.0",
                    "vuln_ids": ["GHSA-demo-1"],
                    "vuln_status": "vulnerable",
                },
            ],
        )
        _write_normalized(
            osv_root,
            hf_model_id="example/model-b",
            model_id="example--model-b--22222222",
            packages=[],
        )
        _write_normalized(
            osv_root,
            hf_model_id="example/model-c",
            model_id="example--model-c--33333333",
            packages=[
                {
                    "dependency_scope": "direct",
                    "ecosystem": "PyPI",
                    "fix_available": True,
                    "manifest_source": "poetry.lock",
                    "max_severity_bucket": "HIGH",
                    "name": "shared-lib",
                    "num_vulns": 1,
                    "version": "2.0.0",
                    "vuln_ids": ["GHSA-demo-1"],
                    "vuln_status": "vulnerable",
                }
            ],
        )

        args = argparse.Namespace(
            input=str(osv_root),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )

        assert run(args) == 0

        graph_path = tmp_path / "graphs" / "global.graphml"
        assert graph_path.exists()

        graph = nx.read_graphml(graph_path)
        model_nodes = [
            node_id
            for node_id, attrs in graph.nodes(data=True)
            if attrs["node_type"] == "Model"
        ]
        package_nodes = [
            node_id
            for node_id, attrs in graph.nodes(data=True)
            if attrs["node_type"] == "Package"
        ]

        assert len(model_nodes) == 3
        assert len(package_nodes) == 2
        assert graph.number_of_edges() == 3

        zero_package_model = next(
            node_id
            for node_id, attrs in graph.nodes(data=True)
            if attrs["node_type"] == "Model"
            and attrs["model_id"] == "example--model-b--22222222"
        )
        assert graph.out_degree(zero_package_model) == 0

        shared_lib_nodes = [
            node_id
            for node_id, attrs in graph.nodes(data=True)
            if attrs["node_type"] == "Package"
            and attrs["name"] == "shared-lib"
            and attrs["version"] == "2.0.0"
        ]
        assert len(shared_lib_nodes) == 1

        shared_edges = [
            attrs
            for source, target, attrs in graph.edges(data=True)
            if target == shared_lib_nodes[0]
        ]
        assert sorted(edge["dependency_scope"] for edge in shared_edges) == ["direct", "transitive"]
        assert sorted(edge["manifest_source"] for edge in shared_edges) == [
            "poetry.lock",
            "requirements.txt",
        ]
