"""Unit tests for dashboard_layout.py."""

from __future__ import annotations

from scripts._utils.dashboard_data import load_dashboard_state
from scripts._utils.dashboard_layout import build_dashboard_layout, build_detail_panel
from scripts._utils.dashboard_theme import DEFAULT_DASHBOARD_THEME
from tests.dashboard_fixtures import write_dashboard_artifacts


def _build_state(tmp_path):
    graph_path, summary_path, table_path = write_dashboard_artifacts(tmp_path)
    return load_dashboard_state(
        graph_path=graph_path,
        summary_path=summary_path,
        table_path=table_path,
    )


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


def test_build_dashboard_layout_exposes_stage_one_shell_regions(tmp_path):
    state = _build_state(tmp_path)

    layout = build_dashboard_layout(state)
    component_ids = _collect_component_ids(layout)

    assert layout.className == "dashboard-page"
    assert layout.style["--atlas-graph-canvas-text"] == (
        DEFAULT_DASHBOARD_THEME.palette.graph_canvas_text
    )
    assert {
        "dashboard-topbar",
        "dashboard-sidebar-left",
        "dashboard-main-pane",
        "dashboard-sidebar-right",
        "search-input",
        "atlas-graph",
        "detail-panel",
        "graph-status-text",
        "selected-node-store",
    }.issubset(component_ids)


def test_build_detail_panel_empty_state_uses_shell_guidance():
    panel = build_detail_panel(
        {
            "kind": "empty",
            "rows": [],
            "subtitle": "Graph explorer",
            "title": "Select a model or package",
            "vulnerability_ids": [],
        }
    )

    assert panel.className == "detail-shell detail-shell-empty"
    assert panel.children[1].children == "Select a model or package"
