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


def _find_component_by_id(component, target_id: str):
    component_id = getattr(component, "id", None)
    if component_id == target_id:
        return component
    children = getattr(component, "children", None)
    if children is None:
        return None
    if isinstance(children, (list, tuple)):
        for child in children:
            found = _find_component_by_id(child, target_id)
            if found is not None:
                return found
        return None
    return _find_component_by_id(children, target_id)


def _collect_links(component) -> list[tuple[str, str, str | None]]:
    found: list[tuple[str, str, str | None]] = []
    href = getattr(component, "href", None)
    if isinstance(href, str):
        found.append((str(getattr(component, "children", "")), href, getattr(component, "target", None)))
    children = getattr(component, "children", None)
    if children is None:
        return found
    if isinstance(children, (list, tuple)):
        for child in children:
            found.extend(_collect_links(child))
        return found
    found.extend(_collect_links(children))
    return found


def _collect_text(component) -> list[str]:
    if isinstance(component, str):
        return [component]
    children = getattr(component, "children", None)
    if children is None:
        return []
    if isinstance(children, (list, tuple)):
        found: list[str] = []
        for child in children:
            found.extend(_collect_text(child))
        return found
    return _collect_text(children)


def test_build_dashboard_layout_exposes_shell_regions_and_bottom_insights(tmp_path):
    state = _build_state(tmp_path)

    layout = build_dashboard_layout(state)
    component_ids = _collect_component_ids(layout)
    left_sidebar = _find_component_by_id(layout, "dashboard-sidebar-left")
    main_pane = _find_component_by_id(layout, "dashboard-main-pane")
    search_input = _find_component_by_id(layout, "search-input")
    topbar = _find_component_by_id(layout, "dashboard-topbar")
    all_text = _collect_text(layout)

    assert layout.className == "dashboard-page"
    assert layout.style["--atlas-graph-canvas-text"] == (
        DEFAULT_DASHBOARD_THEME.palette.graph_canvas_text
    )
    assert {
        "dashboard-topbar",
        "dashboard-sidebar-left",
        "dashboard-main-pane",
        "dashboard-sidebar-right",
        "dashboard-bottom-panels",
        "snapshot-metrics-panel",
        "reuse-hotspots-panel",
        "dashboard-metadata-ribbon",
        "graph-legend",
        "graph-legend-item-model",
        "graph-legend-item-vulnerable",
        "graph-legend-item-unknown",
        "graph-legend-item-safe",
        "search-input",
        "atlas-graph",
        "detail-panel",
        "graph-status-text",
        "selected-node-store",
    }.issubset(component_ids)
    assert left_sidebar is not None
    assert main_pane is not None
    assert search_input is not None
    assert search_input.placeholder == "Hugging Face model or package name"
    assert topbar is not None
    assert "Atlas Graph" not in all_text
    assert (
        "A graph-first local research shell over the validated M1-M4 artifacts. "
        "Filters and details support the atlas without overpowering it."
    ) not in all_text
    assert "snapshot-metrics-panel" not in _collect_component_ids(left_sidebar)
    assert "reuse-hotspots-panel" not in _collect_component_ids(left_sidebar)
    assert {
        "snapshot-metrics-panel",
        "reuse-hotspots-panel",
    }.issubset(_collect_component_ids(main_pane))
    topbar_copy_text = _collect_text(topbar.children[0])
    for expected_text in (
        "AI Supply Chain Risk Atlas",
        "Graph Risk Explorer",
        "Initial scope",
        "Selection",
        "Inspector links",
        "Labels",
    ):
        assert expected_text in topbar_copy_text
    graph_stage = main_pane.children[0].children[0]
    assert graph_stage.className == "graph-stage"
    assert graph_stage.children[0].id == "graph-legend"
    assert len(graph_stage.children[0].children) == 4


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


def test_build_detail_panel_package_links_to_osv_advisories():
    panel = build_detail_panel(
        {
            "kind": "package",
            "rows": [("Package", "shared-lib"), ("Vulnerability count", "2")],
            "subtitle": "PyPI | 1.0.0",
            "title": "shared-lib",
            "vulnerability_ids": ["GHSA-demo-1", "GHSA-demo-2"],
        }
    )

    assert panel.className == "detail-shell"
    assert _collect_links(panel) == [
        (
            "GHSA-demo-1",
            "https://osv.dev/vulnerability/GHSA-demo-1",
            "_blank",
        ),
        (
            "GHSA-demo-2",
            "https://osv.dev/vulnerability/GHSA-demo-2",
            "_blank",
        ),
    ]
