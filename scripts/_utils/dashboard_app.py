"""
dashboard_app.py - Dash app factory and callback wiring for the local showcase.
"""

from __future__ import annotations

from dash import Dash, Input, Output

from scripts._utils.dashboard_controller import compute_dashboard_outputs
from scripts._utils.dashboard_data import DashboardState
from scripts._utils.dashboard_layout import build_dashboard_layout, build_detail_panel
from scripts._utils.dashboard_theme import DASHBOARD_ASSETS_DIR


def build_app(state: DashboardState) -> Dash:
    """Build the single-page Dash app for the atlas showcase."""
    app = Dash(
        __name__,
        assets_folder=str(DASHBOARD_ASSETS_DIR),
        title="AI Supply Chain Risk Atlas",
    )

    app.layout = build_dashboard_layout(state)
    _register_callbacks(app, state)
    return app


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
        outputs = compute_dashboard_outputs(
            state,
            search_text=search_text,
            node_types=node_types,
            dependency_scopes=dependency_scopes,
            vuln_statuses=vuln_statuses,
            severity_buckets=severity_buckets,
            selected_node_id=selected_node_id,
            click_data=click_data,
        )
        return (
            outputs.figure,
            build_detail_panel(outputs.detail_payload),
            outputs.selected_node_id,
            outputs.status_text,
        )
