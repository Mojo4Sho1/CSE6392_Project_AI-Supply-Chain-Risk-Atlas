"""
dashboard_view.py - Pure filter/search/detail helpers for the dashboard.

This module stays renderer-agnostic so future Plotly/Cytoscape swaps do not
touch the canonical view-model logic.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts._utils.dashboard_data import DashboardNode, DashboardState, VisibleGraph

ALL_NODE_TYPES = ("Model", "Package")
ALL_DEPENDENCY_SCOPES = ("direct", "transitive", "unknown")
ALL_VULN_STATUSES = ("vulnerable", "not_vulnerable", "unknown")
ALL_SEVERITY_BUCKETS = ("LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN")


@dataclass(frozen=True)
class DashboardFilters:
    search_text: str = ""
    node_types: tuple[str, ...] = ALL_NODE_TYPES
    dependency_scopes: tuple[str, ...] = ALL_DEPENDENCY_SCOPES
    vuln_statuses: tuple[str, ...] = ALL_VULN_STATUSES
    severity_buckets: tuple[str, ...] = ALL_SEVERITY_BUCKETS


def build_dashboard_filters(
    *,
    search_text: str | None,
    node_types: list[str] | tuple[str, ...] | None,
    dependency_scopes: list[str] | tuple[str, ...] | None,
    vuln_statuses: list[str] | tuple[str, ...] | None,
    severity_buckets: list[str] | tuple[str, ...] | None,
) -> DashboardFilters:
    """Normalize UI inputs into the canonical filter record."""
    return DashboardFilters(
        search_text="" if search_text is None else search_text.strip().lower(),
        node_types=_normalize_filter_values(node_types, ALL_NODE_TYPES),
        dependency_scopes=_normalize_filter_values(
            dependency_scopes,
            ALL_DEPENDENCY_SCOPES,
        ),
        vuln_statuses=_normalize_filter_values(vuln_statuses, ALL_VULN_STATUSES),
        severity_buckets=_normalize_filter_values(severity_buckets, ALL_SEVERITY_BUCKETS),
    )


def build_visible_graph(
    state: DashboardState,
    filters: DashboardFilters,
    *,
    selected_node_id: str | None,
) -> VisibleGraph:
    """Apply search/filter rules and return the canonical visible graph payload."""
    candidate_node_ids = {
        node.node_id
        for node in state.node_lookup.values()
        if _node_matches_intrinsic_filters(node, filters)
    }

    allowed_edges = [
        edge
        for edge in state.edges
        if edge.source in candidate_node_ids
        and edge.target in candidate_node_ids
        and edge.dependency_scope in filters.dependency_scopes
    ]

    if filters.search_text:
        matched_node_ids = {
            node.node_id
            for node in state.node_lookup.values()
            if node.node_id in candidate_node_ids
            and any(filters.search_text in term for term in node.search_terms)
        }
        visible_node_ids = set(matched_node_ids)
        for edge in allowed_edges:
            if edge.source in matched_node_ids or edge.target in matched_node_ids:
                visible_node_ids.add(edge.source)
                visible_node_ids.add(edge.target)
    else:
        visible_node_ids = set(candidate_node_ids)

    visible_edges = [
        edge
        for edge in allowed_edges
        if edge.source in visible_node_ids and edge.target in visible_node_ids
    ]
    resolved_selected_node_id = (
        selected_node_id if selected_node_id in visible_node_ids else None
    )

    return VisibleGraph(
        nodes=[
            state.node_lookup[node_id]
            for node_id in sorted(visible_node_ids, key=lambda value: _node_sort_key(state.node_lookup[value]))
        ],
        edges=sorted(visible_edges, key=lambda edge: (edge.source, edge.target, edge.dependency_scope, edge.manifest_source)),
        selected_node_id=resolved_selected_node_id,
        filters_applied={
            "dependency_scopes": filters.dependency_scopes,
            "node_types": filters.node_types,
            "search_text": filters.search_text,
            "severity_buckets": filters.severity_buckets,
            "vuln_statuses": filters.vuln_statuses,
        },
    )


def build_selection_detail(
    state: DashboardState,
    *,
    selected_node_id: str | None,
) -> dict[str, object]:
    """Build the renderer-agnostic detail payload for the selected node."""
    if selected_node_id is None:
        return {
            "kind": "empty",
            "rows": [],
            "subtitle": "Graph explorer",
            "title": "Select a model or package",
            "vulnerability_ids": [],
        }

    node = state.node_lookup[selected_node_id]
    if node.node_type == "Model":
        return {
            "kind": "model",
            "rows": [
                ("Hugging Face model", str(node.attrs["hf_model_id"])),
                ("Model ID", str(node.attrs["model_id"])),
                ("Direct dependencies", str(node.attrs["direct_dependency_count"])),
                ("Transitive dependencies", str(node.attrs["transitive_dependency_count"])),
                (
                    "Vulnerable direct dependencies",
                    str(node.attrs["vulnerable_direct_dependencies"]),
                ),
                (
                    "Vulnerable transitive dependencies",
                    str(node.attrs["vulnerable_transitive_dependencies"]),
                ),
                ("Unique vulnerability IDs", str(node.attrs["unique_vulnerability_count"])),
            ],
            "subtitle": str(node.attrs["source_repo_url"]),
            "title": str(node.attrs["hf_model_id"]),
            "vulnerability_ids": [],
        }

    version = node.attrs["version"]
    subtitle = f"{node.attrs['ecosystem']} | {'<unversioned>' if version is None else version}"
    return {
        "kind": "package",
        "rows": [
            ("Package", str(node.attrs["name"])),
            ("Ecosystem", str(node.attrs["ecosystem"])),
            ("Version", "<unversioned>" if version is None else str(version)),
            ("Vulnerability status", str(node.attrs["vuln_status"])),
            ("Vulnerability count", str(node.attrs["num_vulns"])),
            ("Severity bucket", str(node.attrs["max_severity_bucket"])),
            ("Fix available", "yes" if bool(node.attrs["fix_available"]) else "no"),
            ("Impacted model count", str(node.attrs["impacted_model_count"])),
        ],
        "subtitle": subtitle,
        "title": str(node.attrs["name"]),
        "vulnerability_ids": list(node.attrs["vuln_ids"]),
    }


def build_graph_status_text(visible_graph: VisibleGraph) -> str:
    """Return a compact status line for the current visible subgraph."""
    return (
        f"Visible graph: {len(visible_graph.nodes)} nodes, "
        f"{len(visible_graph.edges)} edges"
    )


def _normalize_filter_values(
    raw_values: list[str] | tuple[str, ...] | None,
    allowed_values: tuple[str, ...],
) -> tuple[str, ...]:
    if raw_values is None:
        return allowed_values
    normalized = tuple(value for value in allowed_values if value in set(raw_values))
    return normalized


def _node_matches_intrinsic_filters(node: DashboardNode, filters: DashboardFilters) -> bool:
    if node.node_type not in filters.node_types:
        return False
    if node.node_type == "Model":
        return True
    return (
        str(node.attrs["vuln_status"]) in filters.vuln_statuses
        and str(node.attrs["max_severity_bucket"]) in filters.severity_buckets
    )


def _node_sort_key(node: DashboardNode) -> tuple[int, str, str, bool, str]:
    if node.node_type == "Model":
        return (0, str(node.attrs["hf_model_id"]).lower(), str(node.attrs["model_id"]).lower(), False, "")
    version = node.attrs["version"]
    return (
        1,
        str(node.attrs["name"]).lower(),
        str(node.attrs["ecosystem"]).lower(),
        version is not None,
        "" if version is None else str(version),
    )
