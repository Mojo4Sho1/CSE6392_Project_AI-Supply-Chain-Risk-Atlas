"""Integration tests for generate_atlas_reports.py."""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

from scripts._utils.graph_build import build_global_graph, write_graphml_atomic

REPO_ROOT = Path(__file__).parent.parent.parent
SCRIPT = str(REPO_ROOT / "scripts" / "generate_atlas_reports.py")
SNAPSHOT_TS = "2026-03-24T00:00:00Z"


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


def _write_graph(graph_root: Path) -> Path:
    graph = build_global_graph(
        normalized_records=[
            _normalized_record(
                hf_model_id="example/model-a",
                model_id="example--model-a--11111111",
                packages=[
                    _package(
                        name="shared-lib",
                        version="1.0.0",
                        dependency_scope="direct",
                        vuln_status="vulnerable",
                        vuln_ids=["GHSA-demo-1", "GHSA-demo-2"],
                        max_severity_bucket="CRITICAL",
                    ),
                    _package(
                        name="safe-lib",
                        version="2.0.0",
                        dependency_scope="transitive",
                        vuln_status="not_vulnerable",
                    ),
                ],
            ),
            _normalized_record(
                hf_model_id="example/model-b",
                model_id="example--model-b--22222222",
                packages=[
                    _package(
                        name="shared-lib",
                        version="1.0.0",
                        dependency_scope="transitive",
                        vuln_status="vulnerable",
                        vuln_ids=["GHSA-demo-1", "GHSA-demo-2"],
                        max_severity_bucket="CRITICAL",
                    )
                ],
            ),
            _normalized_record(
                hf_model_id="example/model-c",
                model_id="example--model-c--33333333",
                packages=[],
            ),
        ],
        snapshot_timestamp=SNAPSHOT_TS,
    )
    graph_path = graph_root / "global.graphml"
    write_graphml_atomic(graph, graph_path)
    return graph_path


class TestGenerateAtlasReportsCli:
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


class TestGenerateAtlasReportsIntegration:
    def test_generates_summary_csv_and_figures(self, tmp_path):
        from scripts.generate_atlas_reports import run

        graph_path = _write_graph(tmp_path / "graphs")
        args = argparse.Namespace(
            input=str(graph_path),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )

        assert run(args) == 0

        summary_json_path = tmp_path / "reports" / "summary.json"
        summary_csv_path = tmp_path / "reports" / "summary.csv"
        figure_one_path = tmp_path / "figures" / "reused_vulnerable_packages.png"
        figure_two_path = tmp_path / "figures" / "impacted_model_count_distribution.png"

        assert summary_json_path.exists()
        assert summary_csv_path.exists()
        assert figure_one_path.exists()
        assert figure_two_path.exists()

        summary = json.loads(summary_json_path.read_text(encoding="utf-8"))
        assert summary["global_metrics"] == {
            "average_direct_packages_per_model": 1 / 3,
            "average_packages_per_model": 1.0,
            "average_transitive_packages_per_model": 2 / 3,
            "unique_package_count": 2,
        }
        assert [row["hf_model_id"] for row in summary["per_model_metrics"]] == [
            "example/model-a",
            "example/model-b",
            "example/model-c",
        ]
        assert summary["reused_vulnerable_packages"] == [
            {
                "ecosystem": "PyPI",
                "impacted_model_count": 2,
                "name": "shared-lib",
                "version": "1.0.0",
                "vuln_ids": ["GHSA-demo-1", "GHSA-demo-2"],
            }
        ]

        with summary_csv_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert rows == [
            {
                "hf_model_id": "example/model-a",
                "model_id": "example--model-a--11111111",
                "vulnerable_direct_dependencies": "1",
                "vulnerable_transitive_dependencies": "0",
                "vulnerable_packages_per_model": "1",
                "unique_vuln_ids_per_model": "2",
            },
            {
                "hf_model_id": "example/model-b",
                "model_id": "example--model-b--22222222",
                "vulnerable_direct_dependencies": "0",
                "vulnerable_transitive_dependencies": "1",
                "vulnerable_packages_per_model": "1",
                "unique_vuln_ids_per_model": "2",
            },
            {
                "hf_model_id": "example/model-c",
                "model_id": "example--model-c--33333333",
                "vulnerable_direct_dependencies": "0",
                "vulnerable_transitive_dependencies": "0",
                "vulnerable_packages_per_model": "0",
                "unique_vuln_ids_per_model": "0",
            },
        ]

    def test_bad_graph_input_returns_2(self, tmp_path):
        from scripts.generate_atlas_reports import run

        args = argparse.Namespace(
            input=str(tmp_path / "missing.graphml"),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )

        assert run(args) == 2
