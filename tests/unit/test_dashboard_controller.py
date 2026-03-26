"""Unit tests for dashboard_controller.py."""

from __future__ import annotations

from scripts._utils.dashboard_controller import compute_dashboard_outputs
from scripts._utils.dashboard_data import load_dashboard_state
from tests.dashboard_fixtures import write_dashboard_artifacts


def _build_state(tmp_path):
    graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)
    return load_dashboard_state(
        graph_path=graph_path,
        summary_path=summary_path,
        table_path=table_path,
    )


def test_click_selection_overrides_previous_selection(tmp_path):
    state = _build_state(tmp_path)
    previous_selection = state.package_lookup_by_name["shared-lib"][0].node_id

    outputs = compute_dashboard_outputs(
        state,
        search_text="shared-lib",
        node_types=["Model", "Package"],
        dependency_scopes=["direct", "transitive", "unknown"],
        vuln_statuses=["vulnerable", "not_vulnerable", "unknown"],
        severity_buckets=["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"],
        selected_node_id=previous_selection,
        click_data={"points": [{"customdata": "model::example--model-a--11111111"}]},
    )

    assert outputs.selected_node_id == "model::example--model-a--11111111"
    assert outputs.detail_payload["kind"] == "model"
    assert "Visible graph" in outputs.status_text
