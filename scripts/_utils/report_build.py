"""
report_build.py - Helpers for M4 reporting and figure generation.

This module keeps GraphML parsing, metric computation, CSV serialization, and
figure rendering testable without depending on the CLI wrapper.
"""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from collections import Counter
from pathlib import Path

_CACHE_ROOT = Path(tempfile.gettempdir()) / "ai_supply_chain_risk_atlas_cache"
_CACHE_ROOT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_CACHE_ROOT / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(_CACHE_ROOT / "xdg-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

from scripts._utils.graph_build import GraphContractError, validate_graph
from scripts._utils.json_utils import utc_now_iso, write_json_atomic

SCRIPT_SCHEMA_VERSION = "1.0"
SUMMARY_CSV_COLUMNS = [
    "hf_model_id",
    "model_id",
    "vulnerable_direct_dependencies",
    "vulnerable_transitive_dependencies",
    "vulnerable_packages_per_model",
    "unique_vuln_ids_per_model",
]
_TOP_REUSED_PACKAGES_LIMIT = 10


class ReportContractError(Exception):
    """Raised when report input or output violates the M4 contract."""


def load_graph(input_path: str | Path) -> tuple[nx.Graph, Path]:
    """Load and validate the M3 GraphML input."""
    path = Path(input_path)
    if path.is_dir():
        graph_path = path / "global.graphml"
    else:
        graph_path = path

    if not graph_path.exists():
        raise ReportContractError(f"Graph input path does not exist: {graph_path}")

    try:
        graph = nx.read_graphml(graph_path)
    except Exception as exc:
        raise ReportContractError(f"Unable to read GraphML: {graph_path}") from exc

    try:
        validate_graph(graph)
    except GraphContractError as exc:
        raise ReportContractError(f"Graph contract validation failed: {graph_path}") from exc

    return graph, graph_path


def build_summary_payload(*, graph: nx.Graph, graph_source: str | Path) -> dict:
    """Compute the required summary JSON payload from the typed graph."""
    model_nodes = sorted(
        [
            {
                "node_id": node_id,
                "hf_model_id": str(attrs["hf_model_id"]),
                "model_id": str(attrs["model_id"]),
            }
            for node_id, attrs in graph.nodes(data=True)
            if attrs.get("node_type") == "Model"
        ],
        key=lambda item: (item["hf_model_id"], item["model_id"]),
    )
    if not model_nodes:
        raise ReportContractError("Graph contains no Model nodes")

    package_nodes = {
        node_id: _package_record(node_id=node_id, attrs=attrs)
        for node_id, attrs in graph.nodes(data=True)
        if attrs.get("node_type") == "Package"
    }

    per_model_metrics: list[dict] = []
    direct_edge_count = 0
    transitive_edge_count = 0
    total_edge_count = 0

    for model in model_nodes:
        vulnerable_direct = 0
        vulnerable_transitive = 0
        vulnerable_packages = 0
        unique_vuln_ids: set[str] = set()

        out_edges = sorted(
            graph.out_edges(model["node_id"], data=True),
            key=lambda edge: _package_sort_key(package_nodes[edge[1]]),
        )
        for _, package_node_id, edge_attrs in out_edges:
            total_edge_count += 1
            scope = str(edge_attrs.get("dependency_scope"))
            if scope == "direct":
                direct_edge_count += 1
            elif scope == "transitive":
                transitive_edge_count += 1

            package = package_nodes[package_node_id]
            if package["vuln_status"] != "vulnerable":
                continue

            vulnerable_packages += 1
            unique_vuln_ids.update(package["vuln_ids"])
            if scope == "direct":
                vulnerable_direct += 1
            elif scope == "transitive":
                vulnerable_transitive += 1

        per_model_metrics.append(
            {
                "hf_model_id": model["hf_model_id"],
                "model_id": model["model_id"],
                "unique_vuln_ids_per_model": len(unique_vuln_ids),
                "vulnerable_direct_dependencies": vulnerable_direct,
                "vulnerable_packages_per_model": vulnerable_packages,
                "vulnerable_transitive_dependencies": vulnerable_transitive,
            }
        )

    reused_vulnerable_packages: list[dict] = []
    impacted_model_count_distribution: Counter[int] = Counter()
    for package in sorted(package_nodes.values(), key=_package_sort_key):
        if package["vuln_status"] != "vulnerable":
            continue

        impacted_model_count = sum(1 for _ in graph.predecessors(package["node_id"]))
        impacted_model_count_distribution[impacted_model_count] += 1
        reused_vulnerable_packages.append(
            {
                "ecosystem": package["ecosystem"],
                "impacted_model_count": impacted_model_count,
                "name": package["name"],
                "version": package["version"],
                "vuln_ids": package["vuln_ids"],
            }
        )

    reused_vulnerable_packages.sort(key=_reused_package_sort_key)

    snapshot_timestamp = _graph_snapshot_timestamp(graph)
    model_count = len(model_nodes)
    summary = {
        "generated_at_utc": utc_now_iso(),
        "global_metrics": {
            "average_direct_packages_per_model": direct_edge_count / model_count,
            "average_packages_per_model": total_edge_count / model_count,
            "average_transitive_packages_per_model": transitive_edge_count / model_count,
            "unique_package_count": len(package_nodes),
        },
        "graph_source": str(graph_source),
        "per_model_metrics": per_model_metrics,
        "reused_vulnerable_packages": reused_vulnerable_packages,
        "schema_version": SCRIPT_SCHEMA_VERSION,
        "snapshot_timestamp_utc": snapshot_timestamp,
    }
    return summary


def write_summary_json(output_root: str | Path, summary_payload: dict) -> Path:
    """Write reports/summary.json with stable JSON serialization."""
    output_path = Path(output_root) / "reports" / "summary.json"
    write_json_atomic(output_path, summary_payload)
    return output_path


def write_summary_csv(output_root: str | Path, rows: list[dict]) -> Path:
    """Write reports/summary.csv mirroring per_model_metrics order exactly."""
    output_path = Path(output_root) / "reports" / "summary.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=SUMMARY_CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row[column] for column in SUMMARY_CSV_COLUMNS})

    _write_text_atomic(output_path, buffer.getvalue())
    return output_path


def generate_figures(output_root: str | Path, reused_vulnerable_packages: list[dict]) -> list[Path]:
    """Render the minimum required reproducible PNG figure set."""
    figures_dir = Path(output_root) / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    top_reused_path = figures_dir / "reused_vulnerable_packages.png"
    impacted_distribution_path = figures_dir / "impacted_model_count_distribution.png"

    top_reused = reused_vulnerable_packages[:_TOP_REUSED_PACKAGES_LIMIT]
    top_labels = [_format_package_label(item) for item in top_reused]
    top_counts = [item["impacted_model_count"] for item in top_reused]
    _save_figure_atomic(
        top_reused_path,
        lambda fig, ax: _plot_reused_vulnerable_packages(
            fig=fig,
            ax=ax,
            labels=top_labels,
            impacted_counts=top_counts,
        ),
    )

    distribution = Counter(item["impacted_model_count"] for item in reused_vulnerable_packages)
    distribution_points = sorted(distribution.items())
    _save_figure_atomic(
        impacted_distribution_path,
        lambda fig, ax: _plot_impacted_model_count_distribution(
            fig=fig,
            ax=ax,
            points=distribution_points,
        ),
    )

    return [top_reused_path, impacted_distribution_path]


def _graph_snapshot_timestamp(graph: nx.Graph) -> str:
    graph_snapshot = graph.graph.get("snapshot_timestamp_utc")
    if graph_snapshot:
        return str(graph_snapshot)

    snapshots = sorted(
        {
            str(attrs["snapshot_timestamp_utc"])
            for _, attrs in graph.nodes(data=True)
            if attrs.get("node_type") == "Model" and attrs.get("snapshot_timestamp_utc")
        }
    )
    if len(snapshots) != 1:
        raise ReportContractError(
            "Graph must contain exactly one snapshot_timestamp_utc across graph/model metadata"
        )
    return snapshots[0]


def _package_record(*, node_id: str, attrs: dict) -> dict:
    return {
        "ecosystem": str(attrs["ecosystem"]),
        "name": str(attrs["name"]),
        "node_id": node_id,
        "version": _package_version(attrs),
        "vuln_ids": _parse_vuln_ids_json(attrs.get("vuln_ids_json"), node_id=node_id),
        "vuln_status": str(attrs["vuln_status"]),
    }


def _package_version(attrs: dict) -> str | None:
    version_missing = _coerce_bool(attrs.get("version_missing", False))
    raw_version = attrs.get("version")
    if version_missing:
        return None
    if raw_version is None:
        return None
    return str(raw_version)


def _parse_vuln_ids_json(raw_value: object, *, node_id: str) -> list[str]:
    if not isinstance(raw_value, str):
        raise ReportContractError(f"Package node {node_id!r} has non-string vuln_ids_json")
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ReportContractError(
            f"Package node {node_id!r} has invalid vuln_ids_json={raw_value!r}"
        ) from exc
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise ReportContractError(f"Package node {node_id!r} has invalid vuln_ids_json contents")
    return sorted(set(parsed))


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1"}:
            return True
        if normalized in {"false", "0", ""}:
            return False
    raise ReportContractError(f"Boolean-compatible value required, got {value!r}")


def _package_sort_key(package: dict) -> tuple[str, str, bool, str]:
    version = package["version"]
    return (
        package["ecosystem"],
        package["name"],
        version is not None,
        "" if version is None else version,
    )


def _reused_package_sort_key(item: dict) -> tuple[int, str, str, bool, str]:
    version = item["version"]
    return (
        -int(item["impacted_model_count"]),
        item["ecosystem"],
        item["name"],
        version is not None,
        "" if version is None else version,
    )


def _format_package_label(item: dict) -> str:
    version = item["version"] if item["version"] is not None else "<unversioned>"
    return f"{item['ecosystem']}:{item['name']}\n{version}"


def _plot_reused_vulnerable_packages(*, fig, ax, labels: list[str], impacted_counts: list[int]) -> None:
    if not labels:
        _plot_empty_state(fig=fig, ax=ax, title="Top Reused Vulnerable Packages")
        return

    positions = list(range(len(labels)))
    ax.bar(positions, impacted_counts, color="#1f77b4")
    ax.set_title("Top Reused Vulnerable Packages")
    ax.set_xlabel("Package")
    ax.set_ylabel("Impacted model count")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylim(0, max(impacted_counts) + 1)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()


def _plot_impacted_model_count_distribution(*, fig, ax, points: list[tuple[int, int]]) -> None:
    if not points:
        _plot_empty_state(fig=fig, ax=ax, title="Impacted-Model Count Distribution")
        return

    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]
    ax.bar(x_values, y_values, color="#ff7f0e")
    ax.set_title("Impacted-Model Count Distribution")
    ax.set_xlabel("Impacted model count")
    ax.set_ylabel("Vulnerable package count")
    ax.set_xticks(x_values)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()


def _plot_empty_state(*, fig, ax, title: str) -> None:
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        "No vulnerable packages in graph",
        ha="center",
        va="center",
        fontsize=12,
    )
    ax.set_title(title)
    fig.tight_layout()


def _save_figure_atomic(output_path: Path, render_plot) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=output_path.parent, suffix=".tmp.png")
    os.close(fd)
    try:
        figure, axis = plt.subplots(figsize=(10, 6), dpi=200)
        render_plot(figure, axis)
        figure.savefig(tmp_path, dpi=200, bbox_inches="tight", format="png")
        plt.close(figure)
        os.replace(tmp_path, output_path)
    except Exception:
        plt.close("all")
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _write_text_atomic(path: Path, content: str) -> None:
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
