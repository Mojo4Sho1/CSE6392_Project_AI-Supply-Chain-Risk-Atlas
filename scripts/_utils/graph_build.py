"""
graph_build.py - Helpers for M3 graph construction.

This module keeps graph loading, deduplication, and validation logic testable
without depending on the CLI wrapper.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from scripts._utils.json_utils import utc_now_iso

SCRIPT_SCHEMA_VERSION = "1.0"
_SEVERITY_ORDER = {
    "UNKNOWN": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}
_VULN_STATUS_ORDER = {
    "not_vulnerable": 0,
    "unknown": 1,
    "vulnerable": 2,
}
_DEPTH_BY_SCOPE = {
    "direct": 0,
    "transitive": 1,
    "unknown": -1,
}


class GraphContractError(Exception):
    """Raised when graph input or output violates the M3 contract."""


def load_normalized_outputs(input_path: str | Path) -> list[dict]:
    """Load normalized OSV records from a directory or a single file."""
    path = Path(input_path)
    normalized_paths: list[Path]
    if path.is_dir():
        normalized_paths = sorted(path.glob("*/normalized.json"))
    elif path.is_file():
        normalized_paths = [path]
    else:
        raise GraphContractError(f"Input path does not exist: {path}")

    if not normalized_paths:
        raise GraphContractError(f"No normalized.json files found under input path: {path}")

    records: list[dict] = []
    for normalized_path in normalized_paths:
        try:
            record = json.loads(normalized_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise GraphContractError(
                f"Normalized OSV file is not valid JSON: {normalized_path}"
            ) from exc
        except OSError as exc:
            raise GraphContractError(f"Cannot read normalized OSV file: {normalized_path}") from exc

        _validate_normalized_record(record, normalized_path)
        records.append(record)

    records.sort(key=lambda item: (item["hf_model_id"], item["model_id"]))
    return records


def build_global_graph(*, normalized_records: list[dict], snapshot_timestamp: str) -> nx.DiGraph:
    """Build the global typed graph from normalized OSV records."""
    import networkx as nx

    graph = nx.DiGraph()
    graph.graph.update({
        "generated_at_utc": utc_now_iso(),
        "graph_type": "global_risk_atlas",
        "schema_version": SCRIPT_SCHEMA_VERSION,
        "snapshot_timestamp_utc": snapshot_timestamp,
    })

    for record in normalized_records:
        model_node_id = make_model_node_id(record["model_id"])
        model_attrs = {
            "node_type": "Model",
            "model_id": record["model_id"],
            "hf_model_id": record["hf_model_id"],
            "source_repo_url": record["source_repo_url"],
            "snapshot_timestamp_utc": snapshot_timestamp,
        }
        if graph.has_node(model_node_id):
            _validate_same_model_attrs(
                existing=graph.nodes[model_node_id],
                candidate=model_attrs,
                model_id=record["model_id"],
            )
        else:
            graph.add_node(model_node_id, **model_attrs)

        for package in sorted(
            record["packages"],
            key=lambda item: (
                str(item["ecosystem"]).lower(),
                str(item["name"]).lower(),
                "" if item["version"] is None else str(item["version"]),
                item["manifest_source"],
                item["dependency_scope"],
            ),
        ):
            package_key = (
                package["ecosystem"],
                package["name"],
                package["version"],
            )
            package_node_id = make_package_node_id(*package_key)
            package_attrs = _package_node_attrs(package)

            if graph.has_node(package_node_id):
                merged_attrs = _merge_package_node_attrs(
                    existing=graph.nodes[package_node_id],
                    candidate=package_attrs,
                )
                graph.nodes[package_node_id].update(merged_attrs)
            else:
                graph.add_node(package_node_id, **package_attrs)

            graph.add_edge(
                model_node_id,
                package_node_id,
                dependency_scope=package["dependency_scope"],
                depth=_depth_for_scope(package["dependency_scope"]),
                edge_type="uses_package",
                manifest_source=package["manifest_source"],
            )

    validate_graph(graph)
    return graph


def validate_graph(graph: nx.Graph) -> None:
    """Validate required typed graph attributes before or after serialization."""
    for node_id, attrs in graph.nodes(data=True):
        node_type = attrs.get("node_type")
        if node_type == "Model":
            for field in (
                "model_id",
                "hf_model_id",
                "source_repo_url",
                "snapshot_timestamp_utc",
            ):
                if field not in attrs:
                    raise GraphContractError(
                        f"Model node {node_id!r} missing required field {field!r}"
                    )
        elif node_type == "Package":
            for field in (
                "ecosystem",
                "name",
                "version",
                "vuln_status",
                "vuln_ids_json",
                "num_vulns",
                "max_severity_bucket",
                "fix_available",
            ):
                if field not in attrs:
                    raise GraphContractError(
                        f"Package node {node_id!r} missing required field {field!r}"
                    )

            vuln_ids = _parse_vuln_ids_json(attrs["vuln_ids_json"], node_id=node_id)
            num_vulns = _coerce_int(attrs["num_vulns"], field="num_vulns", node_id=node_id)
            if len(vuln_ids) != num_vulns:
                raise GraphContractError(
                    f"Package node {node_id!r} has num_vulns={num_vulns} but "
                    f"{len(vuln_ids)} vuln_ids"
                )
            if attrs["max_severity_bucket"] not in _SEVERITY_ORDER:
                raise GraphContractError(
                    f"Package node {node_id!r} has invalid max_severity_bucket="
                    f"{attrs['max_severity_bucket']!r}"
                )
            if attrs["vuln_status"] not in _VULN_STATUS_ORDER:
                raise GraphContractError(
                    f"Package node {node_id!r} has invalid vuln_status={attrs['vuln_status']!r}"
                )
        else:
            raise GraphContractError(
                f"Node {node_id!r} missing recognized node_type (expected Model or Package)"
            )

    for source, target, attrs in graph.edges(data=True):
        if not graph.has_node(source) or not graph.has_node(target):
            raise GraphContractError(f"Edge ({source!r}, {target!r}) references missing node")
        if graph.nodes[source].get("node_type") != "Model":
            raise GraphContractError(f"uses_package edge source {source!r} is not a Model node")
        if graph.nodes[target].get("node_type") != "Package":
            raise GraphContractError(f"uses_package edge target {target!r} is not a Package node")
        for field in ("edge_type", "dependency_scope", "depth", "manifest_source"):
            if field not in attrs:
                raise GraphContractError(
                    f"Edge ({source!r}, {target!r}) missing required field {field!r}"
                )
        if attrs["edge_type"] != "uses_package":
            raise GraphContractError(
                f"Edge ({source!r}, {target!r}) has unexpected edge_type={attrs['edge_type']!r}"
            )
        scope = attrs["dependency_scope"]
        if scope not in _DEPTH_BY_SCOPE:
            raise GraphContractError(
                f"Edge ({source!r}, {target!r}) has invalid dependency_scope={scope!r}"
            )
        depth = _coerce_int(attrs["depth"], field="depth", node_id=f"{source}->{target}")
        expected_depth = _depth_for_scope(scope)
        if depth != expected_depth:
            raise GraphContractError(
                f"Edge ({source!r}, {target!r}) has depth={depth}; expected {expected_depth} "
                f"for dependency_scope={scope!r}"
            )


def write_graphml_atomic(graph: nx.Graph, output_path: str | Path) -> None:
    """Write GraphML with temp-file then atomic rename semantics."""
    import networkx as nx

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".graphml.tmp")
    os.close(fd)
    try:
        nx.write_graphml(graph, tmp_path)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def make_model_node_id(model_id: str) -> str:
    return f"model::{model_id}"


def make_package_node_id(ecosystem: str, name: str, version: str | None) -> str:
    raw_key = json.dumps(
        [ecosystem, name, version],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    digest = hashlib.sha1(raw_key.encode("utf-8")).hexdigest()[:12]
    return f"package::{digest}"


def _validate_normalized_record(record: dict, normalized_path: Path) -> None:
    required_top_level = [
        "schema_version",
        "generated_at_utc",
        "hf_model_id",
        "model_id",
        "source_repo_url",
        "repo_commit_sha",
        "repo_commit_sha_reason",
        "scanner",
        "packages",
    ]
    for field in required_top_level:
        if field not in record:
            raise GraphContractError(
                f"Normalized OSV file missing required field {field!r}: {normalized_path}"
            )

    if record["schema_version"] != SCRIPT_SCHEMA_VERSION:
        raise GraphContractError(
            f"Unsupported schema_version={record['schema_version']!r} in {normalized_path}"
        )
    if not isinstance(record["packages"], list):
        raise GraphContractError(f"packages must be an array in {normalized_path}")

    scanner = record["scanner"]
    if not isinstance(scanner, dict) or "name" not in scanner or "version" not in scanner:
        raise GraphContractError(f"scanner block missing name/version in {normalized_path}")

    for index, package in enumerate(record["packages"], start=1):
        for field in (
            "ecosystem",
            "name",
            "version",
            "dependency_scope",
            "manifest_source",
            "vuln_status",
            "vuln_ids",
            "num_vulns",
            "max_severity_bucket",
            "fix_available",
        ):
            if field not in package:
                raise GraphContractError(
                    f"Package #{index} missing required field {field!r}: {normalized_path}"
                )
        if package["dependency_scope"] not in _DEPTH_BY_SCOPE:
            raise GraphContractError(
                f"Package #{index} has invalid dependency_scope={package['dependency_scope']!r}: "
                f"{normalized_path}"
            )
        if package["vuln_status"] not in _VULN_STATUS_ORDER:
            raise GraphContractError(
                f"Package #{index} has invalid vuln_status={package['vuln_status']!r}: "
                f"{normalized_path}"
            )
        if package["max_severity_bucket"] not in _SEVERITY_ORDER:
            raise GraphContractError(
                f"Package #{index} has invalid max_severity_bucket="
                f"{package['max_severity_bucket']!r}: {normalized_path}"
            )
        if package["version"] is not None and not isinstance(package["version"], str):
            raise GraphContractError(
                f"Package #{index} version must be a string or null: {normalized_path}"
            )


def _validate_same_model_attrs(*, existing: dict, candidate: dict, model_id: str) -> None:
    for field, value in candidate.items():
        if existing.get(field) != value:
            raise GraphContractError(
                f"Model node conflict for {model_id}: field {field!r} differs between records"
            )


def _package_node_attrs(package: dict) -> dict:
    vuln_ids = sorted(set(package["vuln_ids"]))
    return {
        "ecosystem": package["ecosystem"],
        "fix_available": bool(package["fix_available"]),
        "max_severity_bucket": package["max_severity_bucket"],
        "name": package["name"],
        "node_type": "Package",
        "num_vulns": len(vuln_ids),
        "version": "" if package["version"] is None else package["version"],
        "version_missing": package["version"] is None,
        "vuln_ids_json": json.dumps(vuln_ids, ensure_ascii=False, separators=(",", ":")),
        "vuln_status": package["vuln_status"],
    }


def _merge_package_node_attrs(*, existing: dict, candidate: dict) -> dict:
    for field in ("ecosystem", "name", "version", "version_missing"):
        if existing.get(field) != candidate.get(field):
            raise GraphContractError(
                f"Package node conflict on {field!r}: {existing.get(field)!r} != "
                f"{candidate.get(field)!r}"
            )

    vuln_ids = sorted(
        set(_parse_vuln_ids_json(existing["vuln_ids_json"]))
        | set(_parse_vuln_ids_json(candidate["vuln_ids_json"]))
    )
    return {
        "ecosystem": existing["ecosystem"],
        "fix_available": bool(existing["fix_available"]) or bool(candidate["fix_available"]),
        "max_severity_bucket": _max_severity(
            existing["max_severity_bucket"],
            candidate["max_severity_bucket"],
        ),
        "name": existing["name"],
        "node_type": "Package",
        "num_vulns": len(vuln_ids),
        "version": existing["version"],
        "version_missing": bool(existing["version_missing"]),
        "vuln_ids_json": json.dumps(vuln_ids, ensure_ascii=False, separators=(",", ":")),
        "vuln_status": _max_vuln_status(existing["vuln_status"], candidate["vuln_status"]),
    }


def _parse_vuln_ids_json(raw_value: object, *, node_id: str = "<package>") -> list[str]:
    if not isinstance(raw_value, str):
        raise GraphContractError(f"Package node {node_id!r} has non-string vuln_ids_json")
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise GraphContractError(
            f"Package node {node_id!r} has invalid vuln_ids_json={raw_value!r}"
        ) from exc
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise GraphContractError(
            f"Package node {node_id!r} has non-string entries in vuln_ids_json"
        )
    return parsed


def _coerce_int(raw_value: object, *, field: str, node_id: str) -> int:
    if isinstance(raw_value, bool):
        raise GraphContractError(f"{field} on {node_id!r} must be an integer, not boolean")
    if isinstance(raw_value, int):
        return raw_value
    if isinstance(raw_value, str):
        try:
            return int(raw_value)
        except ValueError as exc:
            raise GraphContractError(
                f"{field} on {node_id!r} must be an integer-compatible value"
            ) from exc
    raise GraphContractError(f"{field} on {node_id!r} must be an integer-compatible value")


def _depth_for_scope(scope: str) -> int:
    return _DEPTH_BY_SCOPE[scope]


def _max_severity(left: str, right: str) -> str:
    return left if _SEVERITY_ORDER[left] >= _SEVERITY_ORDER[right] else right


def _max_vuln_status(left: str, right: str) -> str:
    return left if _VULN_STATUS_ORDER[left] >= _VULN_STATUS_ORDER[right] else right
