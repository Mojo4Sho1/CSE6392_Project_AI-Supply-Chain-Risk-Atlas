"""Unit tests for dashboard_data.py."""

from __future__ import annotations

import json

import pytest

from scripts._utils.dashboard_data import DashboardContractError, load_dashboard_state
from tests.dashboard_fixtures import write_dashboard_artifacts


def test_load_dashboard_state_builds_typed_lookups_and_metrics(tmp_path):
    graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)

    state = load_dashboard_state(
        graph_path=graph_path,
        summary_path=summary_path,
        table_path=table_path,
    )

    assert len(state.node_lookup) == 6
    assert len(state.edges) == 4
    assert set(state.model_lookup_by_model_id) == {
        "example--model-a--11111111",
        "example--model-b--22222222",
        "example--model-c--33333333",
    }

    model_a = state.model_lookup_by_model_id["example--model-a--11111111"]
    assert model_a.attrs["direct_dependency_count"] == 1
    assert model_a.attrs["transitive_dependency_count"] == 1
    assert model_a.attrs["vulnerable_direct_dependencies"] == 1
    assert model_a.attrs["vulnerable_transitive_dependencies"] == 0
    assert model_a.attrs["unique_vulnerability_count"] == 2

    mystery_lib = state.package_lookup_by_name["mystery-lib"][0]
    assert mystery_lib.attrs["version"] is None
    assert mystery_lib.attrs["version_missing"] is True
    assert mystery_lib.attrs["vuln_ids"] == ()

    shared_lib = state.package_lookup_by_name["shared-lib"][0]
    assert shared_lib.attrs["impacted_model_count"] == 2
    assert shared_lib.search_terms[0] == "shared-lib"


def test_load_dashboard_state_layout_positions_are_seeded(tmp_path):
    graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)

    first = load_dashboard_state(
        graph_path=graph_path,
        summary_path=summary_path,
        table_path=table_path,
    )
    second = load_dashboard_state(
        graph_path=graph_path,
        summary_path=summary_path,
        table_path=table_path,
    )

    assert {
        node_id: (node.position_x, node.position_y)
        for node_id, node in first.node_lookup.items()
    } == {
        node_id: (node.position_x, node.position_y)
        for node_id, node in second.node_lookup.items()
    }


def test_load_dashboard_state_rejects_bad_summary_csv_columns(tmp_path):
    graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)
    table_path.write_text("bad,column\nnope,still-bad\n", encoding="utf-8")

    with pytest.raises(DashboardContractError):
        load_dashboard_state(
            graph_path=graph_path,
            summary_path=summary_path,
            table_path=table_path,
        )


def test_load_dashboard_state_rejects_bad_summary_json(tmp_path):
    graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)
    summary_path.write_text(json.dumps({"bad": True}), encoding="utf-8")

    with pytest.raises(DashboardContractError):
        load_dashboard_state(
            graph_path=graph_path,
            summary_path=summary_path,
            table_path=table_path,
        )
