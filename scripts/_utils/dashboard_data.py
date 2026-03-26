"""
dashboard_data.py - Dashboard artifact loading and canonical in-memory state.

This module keeps dashboard input validation, GraphML coercion, layout
calculation, and lookup construction independent from Dash/Plotly so a future
renderer swap does not require rewriting the data layer.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

from scripts._utils.report_build import (
    ReportContractError,
    SUMMARY_CSV_COLUMNS,
    load_graph,
)

_LAYOUT_SEED = 42
_LAYOUT_SCALE = 1000.0
_REQUIRED_SUMMARY_KEYS = {
    "generated_at_utc",
    "global_metrics",
    "graph_source",
    "per_model_metrics",
    "reused_vulnerable_packages",
    "schema_version",
    "snapshot_timestamp_utc",
}
_REQUIRED_GLOBAL_METRIC_KEYS = {
    "average_direct_packages_per_model",
    "average_packages_per_model",
    "average_transitive_packages_per_model",
    "unique_package_count",
}


class DashboardContractError(Exception):
    """Raised when dashboard artifact loading or coercion fails."""


@dataclass(frozen=True)
class DashboardNode:
    node_id: str
    node_type: str
    label: str
    search_terms: tuple[str, ...]
    position_x: float
    position_y: float
    attrs: dict[str, object]


@dataclass(frozen=True)
class DashboardEdge:
    source: str
    target: str
    edge_type: str
    dependency_scope: str
    depth: int
    manifest_source: str


@dataclass(frozen=True)
class VisibleGraph:
    nodes: list[DashboardNode]
    edges: list[DashboardEdge]
    selected_node_id: str | None
    filters_applied: dict[str, object]


@dataclass(frozen=True)
class DashboardState:
    graph: nx.Graph
    graph_path: Path
    summary_path: Path
    table_path: Path
    summary_payload: dict
    summary_table_rows: list[dict[str, str]]
    summary_rows_by_model_id: dict[str, dict[str, str]]
    node_lookup: dict[str, DashboardNode]
    model_lookup_by_model_id: dict[str, DashboardNode]
    model_lookup_by_hf_model_id: dict[str, DashboardNode]
    package_lookup_by_name: dict[str, tuple[DashboardNode, ...]]
    edges: list[DashboardEdge]
    out_edges_by_source: dict[str, tuple[DashboardEdge, ...]]
    in_edges_by_target: dict[str, tuple[DashboardEdge, ...]]


def load_dashboard_state(
    *,
    graph_path: str | Path,
    summary_path: str | Path,
    table_path: str | Path,
) -> DashboardState:
    """Load dashboard artifacts and build the canonical in-memory state."""
    try:
        graph, resolved_graph_path = load_graph(graph_path)
    except ReportContractError as exc:
        raise DashboardContractError(str(exc)) from exc

    resolved_summary_path = Path(summary_path)
    summary_payload = _load_summary_payload(resolved_summary_path)

    resolved_table_path = Path(table_path)
    summary_table_rows = _load_summary_table_rows(resolved_table_path)
    _validate_summary_consistency(graph, summary_payload, summary_table_rows)

    node_positions = _compute_layout_positions(graph)
    edges = _build_edge_records(graph)
    node_lookup = _build_node_lookup(graph, node_positions)

    out_edges_by_source = _group_edges(edges, key="source")
    in_edges_by_target = _group_edges(edges, key="target")

    model_lookup_by_model_id: dict[str, DashboardNode] = {}
    model_lookup_by_hf_model_id: dict[str, DashboardNode] = {}
    package_lookup_by_name_raw: dict[str, list[DashboardNode]] = defaultdict(list)
    summary_rows_by_model_id: dict[str, dict[str, str]] = {}

    for row in summary_table_rows:
        model_id = row["model_id"]
        if model_id in summary_rows_by_model_id:
            raise DashboardContractError(f"Duplicate model_id in summary.csv: {model_id}")
        summary_rows_by_model_id[model_id] = row

    for node in node_lookup.values():
        if node.node_type == "Model":
            model_id = str(node.attrs["model_id"])
            hf_model_id = str(node.attrs["hf_model_id"])
            model_lookup_by_model_id[model_id] = node
            model_lookup_by_hf_model_id[hf_model_id] = node
        else:
            package_lookup_by_name_raw[str(node.attrs["name"]).lower()].append(node)

    package_lookup_by_name = {
        key: tuple(sorted(nodes, key=_package_node_sort_key))
        for key, nodes in package_lookup_by_name_raw.items()
    }

    return DashboardState(
        graph=graph,
        graph_path=resolved_graph_path,
        summary_path=resolved_summary_path,
        table_path=resolved_table_path,
        summary_payload=summary_payload,
        summary_table_rows=summary_table_rows,
        summary_rows_by_model_id=summary_rows_by_model_id,
        node_lookup=node_lookup,
        model_lookup_by_model_id=model_lookup_by_model_id,
        model_lookup_by_hf_model_id=model_lookup_by_hf_model_id,
        package_lookup_by_name=package_lookup_by_name,
        edges=edges,
        out_edges_by_source=out_edges_by_source,
        in_edges_by_target=in_edges_by_target,
    )


def _load_summary_payload(path: Path) -> dict:
    if not path.exists():
        raise DashboardContractError(f"Summary JSON path does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DashboardContractError(f"Summary JSON is not valid JSON: {path}") from exc
    except OSError as exc:
        raise DashboardContractError(f"Cannot read summary JSON: {path}") from exc

    if not isinstance(payload, dict):
        raise DashboardContractError(f"Summary JSON must be an object: {path}")
    missing = sorted(_REQUIRED_SUMMARY_KEYS - set(payload))
    if missing:
        raise DashboardContractError(
            f"Summary JSON missing required fields {missing}: {path}"
        )
    global_metrics = payload.get("global_metrics")
    if not isinstance(global_metrics, dict):
        raise DashboardContractError(f"Summary JSON global_metrics must be an object: {path}")
    missing_metrics = sorted(_REQUIRED_GLOBAL_METRIC_KEYS - set(global_metrics))
    if missing_metrics:
        raise DashboardContractError(
            f"Summary JSON global_metrics missing required fields {missing_metrics}: {path}"
        )
    if not isinstance(payload.get("per_model_metrics"), list):
        raise DashboardContractError(f"Summary JSON per_model_metrics must be an array: {path}")
    if not isinstance(payload.get("reused_vulnerable_packages"), list):
        raise DashboardContractError(
            f"Summary JSON reused_vulnerable_packages must be an array: {path}"
        )
    return payload


def _load_summary_table_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise DashboardContractError(f"Summary CSV path does not exist: {path}")
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != SUMMARY_CSV_COLUMNS:
                raise DashboardContractError(
                    f"Summary CSV columns must equal {SUMMARY_CSV_COLUMNS}, got {reader.fieldnames}"
                )
            return list(reader)
    except OSError as exc:
        raise DashboardContractError(f"Cannot read summary CSV: {path}") from exc


def _validate_summary_consistency(
    graph: nx.Graph,
    summary_payload: dict,
    summary_table_rows: list[dict[str, str]],
) -> None:
    summary_rows = summary_payload["per_model_metrics"]
    if len(summary_rows) != len(summary_table_rows):
        raise DashboardContractError(
            "summary.json and summary.csv disagree on per-model row count"
        )

    summary_model_ids = [str(row["model_id"]) for row in summary_rows]
    csv_model_ids = [str(row["model_id"]) for row in summary_table_rows]
    if summary_model_ids != csv_model_ids:
        raise DashboardContractError("summary.json and summary.csv model order differs")

    graph_model_ids = sorted(
        str(attrs["model_id"])
        for _, attrs in graph.nodes(data=True)
        if attrs.get("node_type") == "Model"
    )
    if sorted(summary_model_ids) != graph_model_ids:
        raise DashboardContractError(
            "graph, summary.json, and summary.csv disagree on the model_id set"
        )


def _compute_layout_positions(graph: nx.Graph) -> dict[str, tuple[float, float]]:
    layout_graph = nx.Graph()
    for node_id in sorted(graph.nodes()):
        layout_graph.add_node(node_id)
    for source, target in sorted((str(source), str(target)) for source, target in graph.edges()):
        layout_graph.add_edge(source, target)

    node_count = max(layout_graph.number_of_nodes(), 1)
    layout = nx.spring_layout(
        layout_graph,
        seed=_LAYOUT_SEED,
        k=1.8 / math.sqrt(node_count),
        iterations=250,
    )
    return {
        node_id: (float(x_coord) * _LAYOUT_SCALE, float(y_coord) * _LAYOUT_SCALE)
        for node_id, (x_coord, y_coord) in layout.items()
    }


def _build_edge_records(graph: nx.Graph) -> list[DashboardEdge]:
    edge_records = [
        DashboardEdge(
            source=str(source),
            target=str(target),
            edge_type=str(attrs["edge_type"]),
            dependency_scope=str(attrs["dependency_scope"]),
            depth=_coerce_int(attrs["depth"], field="depth"),
            manifest_source=str(attrs["manifest_source"]),
        )
        for source, target, attrs in graph.edges(data=True)
    ]
    return sorted(
        edge_records,
        key=lambda edge: (
            edge.source,
            edge.target,
            edge.dependency_scope,
            edge.manifest_source,
        ),
    )


def _build_node_lookup(
    graph: nx.Graph,
    node_positions: dict[str, tuple[float, float]],
) -> dict[str, DashboardNode]:
    node_lookup: dict[str, DashboardNode] = {}
    for node_id, attrs in graph.nodes(data=True):
        position_x, position_y = node_positions[str(node_id)]
        node_type = str(attrs["node_type"])
        if node_type == "Model":
            metrics = _model_metrics(graph, str(node_id))
            hf_model_id = str(attrs["hf_model_id"])
            model_id = str(attrs["model_id"])
            node_lookup[str(node_id)] = DashboardNode(
                node_id=str(node_id),
                node_type="Model",
                label=hf_model_id,
                search_terms=(hf_model_id.lower(), model_id.lower()),
                position_x=position_x,
                position_y=position_y,
                attrs={
                    "direct_dependency_count": metrics["direct_dependency_count"],
                    "hf_model_id": hf_model_id,
                    "model_id": model_id,
                    "snapshot_timestamp_utc": str(attrs["snapshot_timestamp_utc"]),
                    "source_repo_url": str(attrs["source_repo_url"]),
                    "transitive_dependency_count": metrics["transitive_dependency_count"],
                    "unique_vulnerability_count": metrics["unique_vulnerability_count"],
                    "vulnerable_direct_dependencies": metrics["vulnerable_direct_dependencies"],
                    "vulnerable_transitive_dependencies": metrics[
                        "vulnerable_transitive_dependencies"
                    ],
                },
            )
            continue

        package_name = str(attrs["name"])
        version = _package_version(attrs)
        package_label = package_name if version is None else f"{package_name}@{version}"
        node_lookup[str(node_id)] = DashboardNode(
            node_id=str(node_id),
            node_type="Package",
            label=package_label,
            search_terms=tuple(
                term
                for term in (
                    package_name.lower(),
                    package_label.lower(),
                    f"{attrs['ecosystem']}:{package_name}".lower(),
                )
                if term
            ),
            position_x=position_x,
            position_y=position_y,
            attrs={
                "ecosystem": str(attrs["ecosystem"]),
                "fix_available": _coerce_bool(attrs["fix_available"], field="fix_available"),
                "impacted_model_count": int(graph.in_degree(node_id)),
                "max_severity_bucket": str(attrs["max_severity_bucket"]),
                "name": package_name,
                "num_vulns": _coerce_int(attrs["num_vulns"], field="num_vulns"),
                "version": version,
                "version_missing": _coerce_bool(
                    attrs.get("version_missing", False),
                    field="version_missing",
                ),
                "vuln_ids": tuple(_parse_vuln_ids_json(attrs["vuln_ids_json"])),
                "vuln_status": str(attrs["vuln_status"]),
            },
        )
    return node_lookup


def _model_metrics(graph: nx.Graph, node_id: str) -> dict[str, int]:
    direct_dependency_count = 0
    transitive_dependency_count = 0
    vulnerable_direct_dependencies = 0
    vulnerable_transitive_dependencies = 0
    unique_vuln_ids: set[str] = set()

    for _, package_node_id, edge_attrs in graph.out_edges(node_id, data=True):
        scope = str(edge_attrs["dependency_scope"])
        if scope == "direct":
            direct_dependency_count += 1
        elif scope == "transitive":
            transitive_dependency_count += 1

        package_attrs = graph.nodes[package_node_id]
        if str(package_attrs["vuln_status"]) != "vulnerable":
            continue

        unique_vuln_ids.update(_parse_vuln_ids_json(package_attrs["vuln_ids_json"]))
        if scope == "direct":
            vulnerable_direct_dependencies += 1
        elif scope == "transitive":
            vulnerable_transitive_dependencies += 1

    return {
        "direct_dependency_count": direct_dependency_count,
        "transitive_dependency_count": transitive_dependency_count,
        "unique_vulnerability_count": len(unique_vuln_ids),
        "vulnerable_direct_dependencies": vulnerable_direct_dependencies,
        "vulnerable_transitive_dependencies": vulnerable_transitive_dependencies,
    }


def _package_version(attrs: dict) -> str | None:
    version_missing = _coerce_bool(attrs.get("version_missing", False), field="version_missing")
    if version_missing:
        return None
    raw_version = attrs.get("version")
    if raw_version is None:
        return None
    return str(raw_version)


def _parse_vuln_ids_json(raw_value: object) -> list[str]:
    if not isinstance(raw_value, str):
        raise DashboardContractError("Package vuln_ids_json must be a string")
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise DashboardContractError(f"Invalid vuln_ids_json: {raw_value!r}") from exc
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise DashboardContractError("Package vuln_ids_json must contain only strings")
    return sorted(set(parsed))


def _coerce_bool(value: object, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1"}:
            return True
        if normalized in {"false", "0", ""}:
            return False
    raise DashboardContractError(f"{field} must be boolean-compatible, got {value!r}")


def _coerce_int(value: object, *, field: str) -> int:
    if isinstance(value, bool):
        raise DashboardContractError(f"{field} must be integer-compatible, got boolean")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError as exc:
            raise DashboardContractError(
                f"{field} must be integer-compatible, got {value!r}"
            ) from exc
    raise DashboardContractError(f"{field} must be integer-compatible, got {value!r}")


def _group_edges(
    edges: list[DashboardEdge],
    *,
    key: str,
) -> dict[str, tuple[DashboardEdge, ...]]:
    grouped: dict[str, list[DashboardEdge]] = defaultdict(list)
    for edge in edges:
        grouped[getattr(edge, key)].append(edge)
    return {
        node_id: tuple(sorted(grouped_edges, key=_edge_sort_key))
        for node_id, grouped_edges in grouped.items()
    }


def _edge_sort_key(edge: DashboardEdge) -> tuple[str, str, str, str]:
    return (edge.source, edge.target, edge.dependency_scope, edge.manifest_source)


def _package_node_sort_key(node: DashboardNode) -> tuple[str, bool, str]:
    version = node.attrs["version"]
    return (
        str(node.attrs["name"]).lower(),
        version is not None,
        "" if version is None else str(version),
    )
