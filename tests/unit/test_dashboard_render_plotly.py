"""Unit tests for dashboard_render_plotly.py."""

from __future__ import annotations

from copy import deepcopy

from scripts._utils.dashboard_data import load_dashboard_state
from scripts._utils.dashboard_render_plotly import render_visible_graph
from scripts._utils.dashboard_theme import DEFAULT_DASHBOARD_THEME
from scripts._utils.dashboard_view import build_dashboard_filters, build_visible_graph
from tests.dashboard_fixtures import write_dashboard_artifacts


def _build_state(tmp_path):
    graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)
    return load_dashboard_state(
        graph_path=graph_path,
        summary_path=summary_path,
        table_path=table_path,
    )


def test_render_visible_graph_emits_plotly_traces_with_node_ids(tmp_path):
    state = _build_state(tmp_path)
    filters = build_dashboard_filters(
        search_text="",
        node_types=["Model", "Package"],
        dependency_scopes=["direct", "transitive", "unknown"],
        vuln_statuses=["vulnerable", "not_vulnerable", "unknown"],
        severity_buckets=["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"],
    )
    visible_graph = build_visible_graph(state, filters, selected_node_id=None)

    figure = render_visible_graph(visible_graph, state)

    assert len(figure.data) >= 4
    customdata_values = []
    for trace in figure.data:
        if hasattr(trace, "customdata") and trace.customdata is not None:
            customdata_values.extend(list(trace.customdata))
    assert "model::example--model-a--11111111" in customdata_values
    assert state.package_lookup_by_name["shared-lib"][0].node_id in customdata_values
    model_trace = next(trace for trace in figure.data if getattr(trace, "name", None) == "Models")
    assert "model_id=" not in "".join(model_trace.hovertemplate)
    assert figure.layout.plot_bgcolor == DEFAULT_DASHBOARD_THEME.palette.graph_canvas_background
    assert figure.layout.font.color == DEFAULT_DASHBOARD_THEME.palette.graph_canvas_text
    assert figure.layout.showlegend is False


def test_render_visible_graph_does_not_mutate_visible_graph(tmp_path):
    state = _build_state(tmp_path)
    filters = build_dashboard_filters(
        search_text="shared-lib",
        node_types=["Model", "Package"],
        dependency_scopes=["direct", "transitive", "unknown"],
        vuln_statuses=["vulnerable", "not_vulnerable", "unknown"],
        severity_buckets=["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"],
    )
    visible_graph = build_visible_graph(
        state,
        filters,
        selected_node_id=state.package_lookup_by_name["shared-lib"][0].node_id,
    )
    baseline = deepcopy(visible_graph)

    render_visible_graph(visible_graph, state)

    assert visible_graph == baseline
