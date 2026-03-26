"""
dashboard_layout.py - Dash component construction for the current dashboard shell.
"""

from __future__ import annotations

from dash import dcc, html

from scripts._utils.dashboard_controller import compute_dashboard_outputs
from scripts._utils.dashboard_data import DashboardState
from scripts._utils.dashboard_theme import (
    DEFAULT_DASHBOARD_THEME,
    DashboardTheme,
    build_theme_css_variables,
)
from scripts._utils.dashboard_view import (
    ALL_DEPENDENCY_SCOPES,
    ALL_NODE_TYPES,
    ALL_SEVERITY_BUCKETS,
    ALL_VULN_STATUSES,
)


def build_dashboard_layout(
    state: DashboardState,
    *,
    theme: DashboardTheme = DEFAULT_DASHBOARD_THEME,
) -> html.Div:
    """Build the current graph-first dashboard component tree."""
    initial_outputs = compute_dashboard_outputs(
        state,
        search_text="",
        node_types=list(ALL_NODE_TYPES),
        dependency_scopes=list(ALL_DEPENDENCY_SCOPES),
        vuln_statuses=list(ALL_VULN_STATUSES),
        severity_buckets=list(ALL_SEVERITY_BUCKETS),
        selected_node_id=None,
        click_data=None,
    )
    model_count = len(state.model_lookup_by_model_id)
    package_count = int(state.summary_payload["global_metrics"]["unique_package_count"])
    reused_vulnerable_count = len(state.summary_payload["reused_vulnerable_packages"])

    return html.Div(
        className="dashboard-page",
        style=build_theme_css_variables(theme),
        children=[
            dcc.Store(id="selected-node-store", data=initial_outputs.selected_node_id),
            html.Div(
                className="dashboard-shell",
                children=[
                    html.Header(
                        id="dashboard-topbar",
                        className="dashboard-topbar",
                        children=[
                            html.Div(
                                className="topbar-copy",
                                children=[
                                    html.P("AI Supply Chain Risk Atlas", className="eyebrow"),
                                    html.H1("Graph Risk Explorer"),
                                    html.P(
                                        (
                                            "A graph-first local research shell over the validated "
                                            "M1-M4 artifacts. Filters and details support the atlas "
                                            "without overpowering it."
                                        ),
                                        className="header-subtitle",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="topbar-badges",
                                children=[
                                    _topbar_badge("Dataset", f"{model_count} models"),
                                    _topbar_badge("Package nodes", f"{package_count} packages"),
                                    _topbar_badge(
                                        "Reuse hotspots",
                                        f"{reused_vulnerable_count} vulnerable packages",
                                    ),
                                    _topbar_badge("Renderer", "Plotly active"),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="dashboard-workspace",
                        children=[
                            html.Aside(
                                id="dashboard-sidebar-left",
                                className="dashboard-sidebar dashboard-sidebar-left",
                                children=[
                                    html.Section(
                                        id="filters-panel",
                                        className="sidebar-section",
                                        children=[
                                            _panel_heading(
                                                "Search + Filters",
                                                "Narrow the visible graph by entity type, scope, and risk state.",
                                            ),
                                            html.Label(
                                                "Search",
                                                className="control-label",
                                                htmlFor="search-input",
                                            ),
                                            dcc.Input(
                                                id="search-input",
                                                className="text-input",
                                                debounce=True,
                                                placeholder="Hugging Face model or package name",
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
                                ],
                            ),
                            html.Main(
                                id="dashboard-main-pane",
                                className="dashboard-main-pane",
                                children=[
                                    html.Section(
                                        className="graph-panel",
                                        children=[
                                            html.Div(
                                                className="graph-panel-top",
                                                children=[
                                                    _panel_heading(
                                                        "Atlas Graph",
                                                        (
                                                            "Model-package reuse and vulnerability exposure "
                                                            "stay centered, with labels optimized for the "
                                                            "current Plotly renderer."
                                                        ),
                                                    ),
                                                    html.Div(
                                                        className="graph-meta-row",
                                                        children=[
                                                            _context_chip(
                                                                "Initial scope",
                                                                (
                                                                    f"{len(state.node_lookup)} nodes | "
                                                                    f"{len(state.edges)} edges"
                                                                ),
                                                            ),
                                                            _context_chip(
                                                                "Selection",
                                                                "Single-node inspector",
                                                            ),
                                                            _context_chip(
                                                                "Labels",
                                                                "Models default, packages on select",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="graph-stage",
                                                children=[
                                                    dcc.Graph(
                                                        id="atlas-graph",
                                                        className="atlas-graph",
                                                        config={
                                                            "displayModeBar": False,
                                                            "scrollZoom": True,
                                                        },
                                                        figure=initial_outputs.figure,
                                                    )
                                                ],
                                            ),
                                            html.Div(
                                                className="graph-footer",
                                                children=[
                                                    html.P(
                                                        initial_outputs.status_text,
                                                        className="graph-status",
                                                        id="graph-status-text",
                                                    ),
                                                    html.P(
                                                        (
                                                            "Search and filters intersect deterministically "
                                                            "across the live graph and report artifacts."
                                                        ),
                                                        className="graph-caption",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        id="dashboard-bottom-panels",
                                        className="dashboard-bottom-panels",
                                        children=[
                                            html.Section(
                                                id="snapshot-metrics-panel",
                                                className="insight-panel",
                                                children=[
                                                    _panel_heading(
                                                        "Snapshot Metrics",
                                                        (
                                                            "Compact atlas context stays beneath the graph "
                                                            "so the left rail can stay focused on controls."
                                                        ),
                                                    ),
                                                    html.Div(
                                                        className="insight-metric-grid",
                                                        children=[
                                                            _metric_card(
                                                                "Unique packages",
                                                                str(package_count),
                                                                "Shared package nodes in the atlas.",
                                                            ),
                                                            _metric_card(
                                                                "Avg packages / model",
                                                                _format_metric(
                                                                    state.summary_payload["global_metrics"][
                                                                        "average_packages_per_model"
                                                                    ]
                                                                ),
                                                                "Mean dependency footprint.",
                                                            ),
                                                            _metric_card(
                                                                "Avg direct / model",
                                                                _format_metric(
                                                                    state.summary_payload["global_metrics"][
                                                                        "average_direct_packages_per_model"
                                                                    ]
                                                                ),
                                                                "Visible direct package use.",
                                                            ),
                                                            _metric_card(
                                                                "Avg transitive / model",
                                                                _format_metric(
                                                                    state.summary_payload["global_metrics"][
                                                                        "average_transitive_packages_per_model"
                                                                    ]
                                                                ),
                                                                "Visible transitive package use.",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            html.Section(
                                                id="reuse-hotspots-panel",
                                                className="insight-panel",
                                                children=[
                                                    _panel_heading(
                                                        "Reuse Hotspots",
                                                        (
                                                            "Most reused vulnerable packages stay close to "
                                                            "the graph so structural context and reuse context "
                                                            "read together."
                                                        ),
                                                    ),
                                                    html.Div(
                                                        className="table-shell",
                                                        children=[_build_reused_package_table(state)],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Aside(
                                id="dashboard-sidebar-right",
                                className="dashboard-sidebar dashboard-sidebar-right",
                                children=[
                                    html.Section(
                                        className="sidebar-section",
                                        children=[
                                            _panel_heading(
                                                "Selection Inspector",
                                                "Single-node detail context for models and packages.",
                                            ),
                                            html.Div(
                                                className="inspector-note",
                                                children=[
                                                    html.P(
                                                        (
                                                            "Click a node in the graph to inspect dependency "
                                                            "counts, risk metadata, and vulnerability IDs "
                                                            "without leaving the main canvas."
                                                        )
                                                    )
                                                ],
                                            ),
                                            html.Div(
                                                build_detail_panel(initial_outputs.detail_payload),
                                                id="detail-panel",
                                                className="detail-panel-body",
                                            ),
                                        ],
                                    )
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def build_detail_panel(detail_payload: dict[str, object]) -> html.Div:
    """Render the canonical detail payload into Dash components."""
    vulnerability_ids = detail_payload.get("vulnerability_ids", [])
    if detail_payload.get("kind") == "empty":
        return html.Div(
            className="detail-shell detail-shell-empty",
            children=[
                html.P("Inspector Ready", className="detail-kind"),
                html.H3(str(detail_payload["title"]), className="detail-title"),
                html.P(
                    "Use the graph, search, or filters to focus the atlas and inspect one node at a time.",
                    className="detail-subtitle",
                ),
                html.Ul(
                    className="detail-empty-list",
                    children=[
                        html.Li("Model nodes summarize dependency footprint and vulnerable dependencies."),
                        html.Li("Package nodes show status, severity, impacted models, and vulnerability IDs."),
                    ],
                ),
            ],
        )

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
                    html.P("Associated vulnerability IDs", className="detail-section-title"),
                    html.Div(
                        className="detail-chip-list",
                        children=[
                            html.Span(str(vuln_id), className="detail-chip")
                            for vuln_id in vulnerability_ids
                        ],
                    )
                    if vulnerability_ids
                    else html.P(
                        "No vulnerability IDs for the current selection.",
                        className="detail-empty-note",
                    ),
                ],
            ),
        ],
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


def _topbar_badge(label: str, value: str) -> html.Div:
    return html.Div(
        className="topbar-badge",
        children=[
            html.P(label, className="topbar-badge-label"),
            html.P(value, className="topbar-badge-value"),
        ],
    )


def _context_chip(label: str, value: str) -> html.Div:
    return html.Div(
        className="context-chip",
        children=[
            html.Span(label, className="context-chip-label"),
            html.Span(value, className="context-chip-value"),
        ],
    )


def _panel_heading(title: str, subtitle: str) -> html.Div:
    return html.Div(
        className="panel-heading",
        children=[
            html.H2(title),
            html.P(subtitle),
        ],
    )


def _build_reused_package_table(state: DashboardState) -> html.Table:
    top_packages = state.summary_payload["reused_vulnerable_packages"][:8]
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
        body_rows.append(html.Tr([html.Td("No vulnerable packages", colSpan=3)]))
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


def _format_metric(value: object) -> str:
    return f"{float(value):.2f}"
