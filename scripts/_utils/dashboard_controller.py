"""
dashboard_controller.py - Renderer-agnostic orchestration for dashboard state.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts._utils.dashboard_data import DashboardState
from scripts._utils.dashboard_render_plotly import render_visible_graph
from scripts._utils.dashboard_view import (
    build_dashboard_filters,
    build_graph_status_text,
    build_selection_detail,
    build_visible_graph,
)


@dataclass(frozen=True)
class DashboardOutputs:
    figure: object
    detail_payload: dict[str, object]
    selected_node_id: str | None
    status_text: str


def compute_dashboard_outputs(
    state: DashboardState,
    *,
    search_text: str | None,
    node_types: list[str] | tuple[str, ...] | None,
    dependency_scopes: list[str] | tuple[str, ...] | None,
    vuln_statuses: list[str] | tuple[str, ...] | None,
    severity_buckets: list[str] | tuple[str, ...] | None,
    selected_node_id: str | None,
    click_data: dict | None,
) -> DashboardOutputs:
    """Compute the canonical dashboard outputs from the current interaction state."""
    clicked_node_id = _extract_clicked_node_id(click_data)
    resolved_selected_node_id = clicked_node_id or selected_node_id
    filters = build_dashboard_filters(
        search_text=search_text,
        node_types=node_types,
        dependency_scopes=dependency_scopes,
        vuln_statuses=vuln_statuses,
        severity_buckets=severity_buckets,
    )
    visible_graph = build_visible_graph(
        state,
        filters,
        selected_node_id=resolved_selected_node_id,
    )
    return DashboardOutputs(
        figure=render_visible_graph(visible_graph, state),
        detail_payload=build_selection_detail(
            state,
            selected_node_id=visible_graph.selected_node_id,
        ),
        selected_node_id=visible_graph.selected_node_id,
        status_text=build_graph_status_text(visible_graph),
    )


def _extract_clicked_node_id(click_data: dict | None) -> str | None:
    if not click_data:
        return None
    points = click_data.get("points")
    if not isinstance(points, list) or not points:
        return None
    raw_value = points[0].get("customdata")
    if raw_value is None:
        return None
    return str(raw_value)
