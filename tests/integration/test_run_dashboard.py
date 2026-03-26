"""Integration tests for run_dashboard.py."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from tests.dashboard_fixtures import write_dashboard_artifacts

REPO_ROOT = Path(__file__).parent.parent.parent
SCRIPT = str(REPO_ROOT / "scripts" / "run_dashboard.py")


def _collect_component_ids(component) -> set[str]:
    found: set[str] = set()
    component_id = getattr(component, "id", None)
    if isinstance(component_id, str):
        found.add(component_id)
    children = getattr(component, "children", None)
    if children is None:
        return found
    if isinstance(children, (list, tuple)):
        for child in children:
            found.update(_collect_component_ids(child))
        return found
    found.update(_collect_component_ids(children))
    return found


class TestRunDashboardCli:
    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, SCRIPT, "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        assert "--graph" in result.stdout
        assert "--summary" in result.stdout
        assert "--table" in result.stdout
        assert "--host" in result.stdout
        assert "--port" in result.stdout


class TestRunDashboardIntegration:
    def test_run_returns_2_for_missing_graph(self, tmp_path):
        from scripts.run_dashboard import run

        args = argparse.Namespace(
            graph=str(tmp_path / "missing.graphml"),
            host="127.0.0.1",
            log_level="WARNING",
            port=8050,
            summary=str(tmp_path / "missing-summary.json"),
            table=str(tmp_path / "missing-summary.csv"),
        )

        assert run(args, serve=False) == 2

    def test_startup_succeeds_and_app_layout_contains_required_sections(self, tmp_path):
        from scripts._utils.dashboard_app import build_app, compute_dashboard_outputs
        from scripts._utils.dashboard_data import load_dashboard_state
        from scripts.run_dashboard import run

        graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)
        state = load_dashboard_state(
            graph_path=graph_path,
            summary_path=summary_path,
            table_path=table_path,
        )
        app = build_app(state)
        component_ids = _collect_component_ids(app.layout)

        assert {
            "search-input",
            "node-type-filter",
            "dependency-scope-filter",
            "vuln-status-filter",
            "severity-filter",
            "atlas-graph",
            "detail-panel",
            "graph-status-text",
            "selected-node-store",
        }.issubset(component_ids)

        figure, detail_panel, selected_node_id, status_text = compute_dashboard_outputs(
            state,
            search_text="shared-lib",
            node_types=["Model", "Package"],
            dependency_scopes=["direct", "transitive", "unknown"],
            vuln_statuses=["vulnerable", "not_vulnerable", "unknown"],
            severity_buckets=["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"],
            selected_node_id=None,
            click_data={"points": [{"customdata": "model::example--model-a--11111111"}]},
        )

        assert len(figure.data) >= 2
        assert selected_node_id == "model::example--model-a--11111111"
        assert "Visible graph" in status_text
        assert getattr(detail_panel, "children", None) is not None

        args = argparse.Namespace(
            graph=str(graph_path),
            host="127.0.0.1",
            log_level="WARNING",
            port=8050,
            summary=str(summary_path),
            table=str(table_path),
        )
        assert run(args, serve=False) == 0
