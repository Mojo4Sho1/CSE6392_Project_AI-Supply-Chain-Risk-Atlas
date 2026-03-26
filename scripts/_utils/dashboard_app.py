"""
dashboard_app.py - Dash app factory and callback wiring for the local showcase.
"""

from __future__ import annotations

from dash import Dash, Input, Output, dcc, html

from scripts._utils.dashboard_data import DashboardState
from scripts._utils.dashboard_render_plotly import render_visible_graph
from scripts._utils.dashboard_view import (
    ALL_DEPENDENCY_SCOPES,
    ALL_NODE_TYPES,
    ALL_SEVERITY_BUCKETS,
    ALL_VULN_STATUSES,
    build_dashboard_filters,
    build_graph_status_text,
    build_selection_detail,
    build_visible_graph,
)


def build_app(state: DashboardState) -> Dash:
    """Build the single-page Dash app for the atlas showcase."""
    app = Dash(
        __name__,
        title="AI Supply Chain Risk Atlas",
    )

    app.layout = _build_layout(state)
    _register_callbacks(app, state)
    return app


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
) -> tuple[object, object, str | None, str]:
    """Compute the full dashboard output set from the current interaction state."""
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
    figure = render_visible_graph(visible_graph, state)
    detail_payload = build_selection_detail(
        state,
        selected_node_id=visible_graph.selected_node_id,
    )
    detail_panel = _build_detail_panel(detail_payload)
    return (
        figure,
        detail_panel,
        visible_graph.selected_node_id,
        build_graph_status_text(visible_graph),
    )


def _build_layout(state: DashboardState) -> html.Div:
    initial_figure, initial_detail, initial_selection, initial_status = compute_dashboard_outputs(
        state,
        search_text="",
        node_types=list(ALL_NODE_TYPES),
        dependency_scopes=list(ALL_DEPENDENCY_SCOPES),
        vuln_statuses=list(ALL_VULN_STATUSES),
        severity_buckets=list(ALL_SEVERITY_BUCKETS),
        selected_node_id=None,
        click_data=None,
    )

    return html.Div(
        className="dashboard-shell",
        children=[
            dcc.Store(id="selected-node-store", data=initial_selection),
            html.Header(
                className="dashboard-header",
                children=[
                    html.P("AI Supply Chain Risk Atlas", className="eyebrow"),
                    html.H1("Local Showcase Dashboard"),
                    html.P(
                        "A single-page explorer over the validated M1-M4 graph and report artifacts.",
                        className="header-subtitle",
                    ),
                ],
            ),
            html.Section(
                className="overview-grid",
                children=[
                    _metric_card(
                        "Unique packages",
                        str(state.summary_payload["global_metrics"]["unique_package_count"]),
                        "Global package node count from the typed atlas graph.",
                    ),
                    _metric_card(
                        "Avg packages / model",
                        _format_metric(
                            state.summary_payload["global_metrics"]["average_packages_per_model"]
                        ),
                        "Mean model dependency footprint across the sample.",
                    ),
                    _metric_card(
                        "Avg direct / model",
                        _format_metric(
                            state.summary_payload["global_metrics"][
                                "average_direct_packages_per_model"
                            ]
                        ),
                        "Direct dependency mean from visible M3 edges.",
                    ),
                    _metric_card(
                        "Avg transitive / model",
                        _format_metric(
                            state.summary_payload["global_metrics"][
                                "average_transitive_packages_per_model"
                            ]
                        ),
                        "Transitive dependency mean from visible M3 edges.",
                    ),
                    html.Div(
                        className="overview-table-card",
                        children=[
                            html.Div(
                                className="panel-heading",
                                children=[
                                    html.H2("Top Reused Vulnerable Packages"),
                                    html.P("From reports/summary.json"),
                                ],
                            ),
                            _build_reused_package_table(state),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="workspace-grid",
                children=[
                    html.Aside(
                        className="filter-panel",
                        children=[
                            html.Div(
                                className="panel-heading",
                                children=[
                                    html.H2("Filters"),
                                    html.P("Search, scope, and risk-state controls."),
                                ],
                            ),
                            html.Label("Search", className="control-label", htmlFor="search-input"),
                            dcc.Input(
                                id="search-input",
                                className="text-input",
                                debounce=True,
                                placeholder="hf_model_id, model_id, or package name",
                                type="text",
                                value="",
                            ),
                            _checklist_block(
                                "Node type",
                                "node-type-filter",
                                ALL_NODE_TYPES,
                                list(ALL_NODE_TYPES),
                            ),
                            _checklist_block(
                                "Dependency scope",
                                "dependency-scope-filter",
                                ALL_DEPENDENCY_SCOPES,
                                list(ALL_DEPENDENCY_SCOPES),
                            ),
                            _checklist_block(
                                "Vulnerability status",
                                "vuln-status-filter",
                                ALL_VULN_STATUSES,
                                list(ALL_VULN_STATUSES),
                            ),
                            _checklist_block(
                                "Severity bucket",
                                "severity-filter",
                                ALL_SEVERITY_BUCKETS,
                                list(ALL_SEVERITY_BUCKETS),
                            ),
                        ],
                    ),
                    html.Div(
                        className="graph-panel",
                        children=[
                            html.Div(
                                className="panel-heading",
                                children=[
                                    html.H2("Graph Explorer"),
                                    html.P("Models stay labeled by default; packages surface labels when selected."),
                                ],
                            ),
                            dcc.Graph(
                                id="atlas-graph",
                                className="atlas-graph",
                                config={"displayModeBar": False, "scrollZoom": True},
                                figure=initial_figure,
                            ),
                            html.P(initial_status, className="graph-status", id="graph-status-text"),
                        ],
                    ),
                    html.Aside(
                        className="detail-panel",
                        children=[
                            html.Div(
                                className="panel-heading",
                                children=[
                                    html.H2("Detail View"),
                                    html.P("Selection-driven model and package inspection."),
                                ],
                            ),
                            html.Div(initial_detail, id="detail-panel"),
                        ],
                    ),
                ],
            ),
        ],
    )


def _register_callbacks(app: Dash, state: DashboardState) -> None:
    @app.callback(
        Output("atlas-graph", "figure"),
        Output("detail-panel", "children"),
        Output("selected-node-store", "data"),
        Output("graph-status-text", "children"),
        Input("search-input", "value"),
        Input("node-type-filter", "value"),
        Input("dependency-scope-filter", "value"),
        Input("vuln-status-filter", "value"),
        Input("severity-filter", "value"),
        Input("atlas-graph", "clickData"),
        Input("selected-node-store", "data"),
    )
    def _refresh_dashboard(
        search_text,
        node_types,
        dependency_scopes,
        vuln_statuses,
        severity_buckets,
        click_data,
        selected_node_id,
    ):
        return compute_dashboard_outputs(
            state,
            search_text=search_text,
            node_types=node_types,
            dependency_scopes=dependency_scopes,
            vuln_statuses=vuln_statuses,
            severity_buckets=severity_buckets,
            selected_node_id=selected_node_id,
            click_data=click_data,
        )


def _metric_card(title: str, value: str, description: str) -> html.Div:
    return html.Div(
        className="metric-card",
        children=[
            html.P(title, className="metric-label"),
            html.P(value, className="metric-value"),
            html.P(description, className="metric-description"),
        ],
    )


def _build_reused_package_table(state: DashboardState) -> html.Table:
    top_packages = state.summary_payload["reused_vulnerable_packages"][:10]
    header = html.Thead(
        html.Tr(
            [
                html.Th("Package"),
                html.Th("Version"),
                html.Th("Impacted models"),
            ]
        )
    )
    body_rows = []
    for item in top_packages:
        body_rows.append(
            html.Tr(
                [
                    html.Td(f"{item['ecosystem']}:{item['name']}"),
                    html.Td("<unversioned>" if item["version"] is None else str(item["version"])),
                    html.Td(str(item["impacted_model_count"])),
                ]
            )
        )
    if not body_rows:
        body_rows.append(
            html.Tr([html.Td("No vulnerable packages", colSpan=3)])
        )
    return html.Table(className="overview-table", children=[header, html.Tbody(body_rows)])


def _checklist_block(
    title: str,
    component_id: str,
    values: tuple[str, ...],
    default: list[str],
) -> html.Div:
    return html.Div(
        className="checklist-block",
        children=[
            html.P(title, className="control-label"),
            dcc.Checklist(
                id=component_id,
                className="checklist",
                inputClassName="checklist-input",
                labelClassName="checklist-label",
                options=[{"label": value, "value": value} for value in values],
                value=default,
            ),
        ],
    )


def _build_detail_panel(detail_payload: dict[str, object]) -> html.Div:
    vulnerability_ids = detail_payload.get("vulnerability_ids", [])
    return html.Div(
        className="detail-shell",
        children=[
            html.P(str(detail_payload["kind"]).upper(), className="detail-kind"),
            html.H3(str(detail_payload["title"]), className="detail-title"),
            html.P(str(detail_payload["subtitle"]), className="detail-subtitle"),
            html.Div(
                className="detail-metric-list",
                children=[
                    html.Div(
                        className="detail-metric-row",
                        children=[
                            html.Span(str(label), className="detail-metric-label"),
                            html.Span(str(value), className="detail-metric-value"),
                        ],
                    )
                    for label, value in detail_payload["rows"]
                ],
            ),
            html.Div(
                className="detail-vulns",
                children=[
                    html.P("Associated vulnerability IDs", className="control-label"),
                    html.Ul(
                        [html.Li(vuln_id) for vuln_id in vulnerability_ids]
                        if vulnerability_ids
                        else [html.Li("No vulnerability IDs for the current selection.")],
                    ),
                ],
            ),
        ],
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


def _format_metric(value: object) -> str:
    return f"{float(value):.2f}"
