"""Unit tests for dashboard_view.py."""

from __future__ import annotations

from scripts._utils.dashboard_data import load_dashboard_state
from scripts._utils.dashboard_view import (
    build_dashboard_filters,
    build_selection_detail,
    build_visible_graph,
)
from tests.dashboard_fixtures import write_dashboard_artifacts


def _build_state(tmp_path):
    graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)
    return load_dashboard_state(
        graph_path=graph_path,
        summary_path=summary_path,
        table_path=table_path,
    )


def test_search_by_model_includes_adjacent_packages_and_edges(tmp_path):
    state = _build_state(tmp_path)
    filters = build_dashboard_filters(
        search_text="model-a",
        node_types=["Model", "Package"],
        dependency_scopes=["direct", "transitive", "unknown"],
        vuln_statuses=["vulnerable", "not_vulnerable", "unknown"],
        severity_buckets=["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"],
    )

    visible_graph = build_visible_graph(state, filters, selected_node_id=None)
    visible_node_ids = {node.node_id for node in visible_graph.nodes}

    assert "model::example--model-a--11111111" in visible_node_ids
    assert len(visible_graph.edges) == 2
    assert any(node.attrs.get("name") == "shared-lib" for node in visible_graph.nodes)
    assert any(node.attrs.get("name") == "safe-lib" for node in visible_graph.nodes)


def test_search_by_package_includes_adjacent_models(tmp_path):
    state = _build_state(tmp_path)
    filters = build_dashboard_filters(
        search_text="shared-lib",
        node_types=["Model", "Package"],
        dependency_scopes=["direct", "transitive", "unknown"],
        vuln_statuses=["vulnerable", "not_vulnerable", "unknown"],
        severity_buckets=["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"],
    )

    visible_graph = build_visible_graph(state, filters, selected_node_id=None)
    visible_labels = {node.label for node in visible_graph.nodes}

    assert "shared-lib@1.0.0" in visible_labels
    assert "example/model-a" in visible_labels
    assert "example/model-b" in visible_labels
    assert len(visible_graph.edges) == 2


def test_multi_filter_intersection_preserves_selection_when_visible(tmp_path):
    state = _build_state(tmp_path)
    selected_package_node_id = state.package_lookup_by_name["shared-lib"][0].node_id
    filters = build_dashboard_filters(
        search_text="",
        node_types=["Model", "Package"],
        dependency_scopes=["transitive"],
        vuln_statuses=["vulnerable"],
        severity_buckets=["HIGH"],
    )

    visible_graph = build_visible_graph(
        state,
        filters,
        selected_node_id=selected_package_node_id,
    )

    assert visible_graph.selected_node_id == selected_package_node_id
    assert len(visible_graph.edges) == 1
    assert visible_graph.edges[0].dependency_scope == "transitive"


def test_selection_clears_when_filtered_out(tmp_path):
    state = _build_state(tmp_path)
    selected_package_node_id = state.package_lookup_by_name["mystery-lib"][0].node_id
    filters = build_dashboard_filters(
        search_text="",
        node_types=["Model", "Package"],
        dependency_scopes=["direct", "transitive", "unknown"],
        vuln_statuses=["vulnerable"],
        severity_buckets=["HIGH"],
    )

    visible_graph = build_visible_graph(
        state,
        filters,
        selected_node_id=selected_package_node_id,
    )

    assert visible_graph.selected_node_id is None


def test_build_selection_detail_for_model_and_package(tmp_path):
    state = _build_state(tmp_path)
    model_node_id = state.model_lookup_by_model_id["example--model-a--11111111"].node_id
    package_node_id = state.package_lookup_by_name["shared-lib"][0].node_id

    model_detail = build_selection_detail(state, selected_node_id=model_node_id)
    package_detail = build_selection_detail(state, selected_node_id=package_node_id)

    assert model_detail["kind"] == "model"
    assert ("Model ID", "example--model-a--11111111") not in model_detail["rows"]
    assert ("Hugging Face model", "example/model-a") not in model_detail["rows"]
    assert ("Direct dependencies", "1") in model_detail["rows"]
    assert package_detail["kind"] == "package"
    assert ("Impacted model count", "2") in package_detail["rows"]
    assert package_detail["vulnerability_ids"] == ["GHSA-demo-1", "GHSA-demo-2"]
