"""
dashboard_render_plotly.py - Plotly renderer for the canonical dashboard view.
"""

from __future__ import annotations

import plotly.graph_objects as go

from scripts._utils.dashboard_data import DashboardNode, DashboardState, VisibleGraph

_MODEL_COLOR = "#0f766e"
_MODEL_OUTLINE = "#0b3f3a"
_EDGE_COLOR = "rgba(15, 23, 42, 0.18)"
_SELECTED_COLOR = "#f97316"
_PACKAGE_COLORS = {
    "not_vulnerable": "#22c55e",
    "unknown": "#f59e0b",
    "vulnerable": "#dc2626",
}


def render_visible_graph(
    visible_graph: VisibleGraph,
    dashboard_state: DashboardState,
) -> go.Figure:
    """Render the visible graph using only canonical node/edge records."""
    del dashboard_state  # Renderer v1 only needs the canonical visible graph payload.

    figure = go.Figure()
    node_lookup = {node.node_id: node for node in visible_graph.nodes}

    if visible_graph.edges:
        edge_x: list[float | None] = []
        edge_y: list[float | None] = []
        for edge in visible_graph.edges:
            source_node = node_lookup[edge.source]
            target_node = node_lookup[edge.target]
            edge_x.extend([source_node.position_x, target_node.position_x, None])
            edge_y.extend([source_node.position_y, target_node.position_y, None])
        figure.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                hoverinfo="skip",
                line={"color": _EDGE_COLOR, "width": 1.0},
                mode="lines",
                name="uses_package",
                showlegend=False,
            )
        )

    package_groups = {
        status: [
            node
            for node in visible_graph.nodes
            if node.node_type == "Package" and str(node.attrs["vuln_status"]) == status
        ]
        for status in ("vulnerable", "unknown", "not_vulnerable")
    }
    for vuln_status, package_nodes in package_groups.items():
        if not package_nodes:
            continue
        figure.add_trace(
            go.Scatter(
                x=[node.position_x for node in package_nodes],
                y=[node.position_y for node in package_nodes],
                customdata=[node.node_id for node in package_nodes],
                hovertemplate=_package_hover_template(package_nodes),
                marker={
                    "color": _PACKAGE_COLORS[vuln_status],
                    "line": {"color": "rgba(15,23,42,0.35)", "width": 1},
                    "opacity": 0.85,
                    "size": [_package_marker_size(node) for node in package_nodes],
                },
                mode="markers",
                name=f"Packages: {vuln_status}",
                showlegend=True,
            )
        )

    model_nodes = [node for node in visible_graph.nodes if node.node_type == "Model"]
    if model_nodes:
        figure.add_trace(
            go.Scatter(
                x=[node.position_x for node in model_nodes],
                y=[node.position_y for node in model_nodes],
                customdata=[node.node_id for node in model_nodes],
                hovertemplate=_model_hover_template(model_nodes),
                marker={
                    "color": _MODEL_COLOR,
                    "line": {"color": _MODEL_OUTLINE, "width": 1.6},
                    "opacity": [
                        0.95 if _model_has_visible_edge(node, visible_graph) else 0.45
                        for node in model_nodes
                    ],
                    "size": 19,
                    "symbol": "diamond",
                },
                mode="markers+text",
                name="Models",
                showlegend=True,
                text=[str(node.attrs["hf_model_id"]) for node in model_nodes],
                textfont={"color": "#0f172a", "family": "Avenir Next, Trebuchet MS, sans-serif", "size": 11},
                textposition="top center",
            )
        )

    selected_node = (
        node_lookup.get(visible_graph.selected_node_id)
        if visible_graph.selected_node_id is not None
        else None
    )
    if selected_node is not None:
        figure.add_trace(
            go.Scatter(
                x=[selected_node.position_x],
                y=[selected_node.position_y],
                customdata=[selected_node.node_id],
                hoverinfo="skip",
                marker={
                    "color": _SELECTED_COLOR,
                    "line": {"color": "#7c2d12", "width": 2},
                    "size": 26 if selected_node.node_type == "Model" else 22,
                    "symbol": "circle-open-dot",
                },
                mode="markers+text",
                name="Selected",
                showlegend=False,
                text=[selected_node.label],
                textfont={"color": "#9a3412", "family": "Avenir Next, Trebuchet MS, sans-serif", "size": 12},
                textposition="bottom center",
            )
        )

    figure.update_layout(
        clickmode="event+select",
        dragmode="pan",
        hovermode="closest",
        legend={
            "bgcolor": "rgba(255,255,255,0.78)",
            "bordercolor": "rgba(15,23,42,0.08)",
            "borderwidth": 1,
            "orientation": "h",
            "x": 0.0,
            "y": 1.02,
        },
        margin={"b": 16, "l": 16, "r": 16, "t": 16},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.9)",
        uirevision="atlas-dashboard-v1",
        xaxis={"showgrid": False, "showticklabels": False, "zeroline": False},
        yaxis={"showgrid": False, "showticklabels": False, "zeroline": False},
    )

    if not visible_graph.nodes:
        figure.add_annotation(
            showarrow=False,
            text="No nodes match the current search and filters.",
            x=0.5,
            xref="paper",
            y=0.5,
            yref="paper",
            font={"color": "#475569", "family": "Avenir Next, Trebuchet MS, sans-serif", "size": 14},
        )

    return figure


def _package_marker_size(node: DashboardNode) -> int:
    impacted_model_count = int(node.attrs["impacted_model_count"])
    return 11 + (impacted_model_count * 4)


def _model_has_visible_edge(node: DashboardNode, visible_graph: VisibleGraph) -> bool:
    return any(
        edge.source == node.node_id or edge.target == node.node_id
        for edge in visible_graph.edges
    )


def _model_hover_template(model_nodes: list[DashboardNode]) -> list[str]:
    return [
        (
            f"<b>{node.attrs['hf_model_id']}</b><br>"
            f"model_id={node.attrs['model_id']}<br>"
            f"direct={node.attrs['direct_dependency_count']} | "
            f"transitive={node.attrs['transitive_dependency_count']}<br>"
            f"vulnerable direct={node.attrs['vulnerable_direct_dependencies']} | "
            f"vulnerable transitive={node.attrs['vulnerable_transitive_dependencies']}"
            "<extra></extra>"
        )
        for node in model_nodes
    ]


def _package_hover_template(package_nodes: list[DashboardNode]) -> list[str]:
    templates: list[str] = []
    for node in package_nodes:
        version = node.attrs["version"]
        version_text = "<unversioned>" if version is None else str(version)
        templates.append(
            (
                f"<b>{node.attrs['name']}</b><br>"
                f"{node.attrs['ecosystem']} | {version_text}<br>"
                f"status={node.attrs['vuln_status']} | "
                f"severity={node.attrs['max_severity_bucket']}<br>"
                f"impacted models={node.attrs['impacted_model_count']}"
                "<extra></extra>"
            )
        )
    return templates
