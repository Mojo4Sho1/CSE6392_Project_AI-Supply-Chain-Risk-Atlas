"""
osv_scan.py - Helpers for M2 OSV scanning and normalization.

This module keeps artifact parsing and raw-to-normalized transformation
logic testable without requiring live scanner execution.
"""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


_PINNED_REQUIREMENT_RE = re.compile(
    r"^\s*([A-Za-z0-9_.-]+(?:\[[^\]]+\])?)\s*(===|==)\s*([^\s;,#]+)\s*$"
)
_REQUIREMENT_NAME_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+(?:\[[^\]]+\])?)")
_CANONICALIZE_PYPI_RE = re.compile(r"[-_.]+")
_SEVERITY_ORDER = {
    "UNKNOWN": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}
_SEMVER_EXACT_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z.+-]*$")
_VERSION_OUTPUT_RE = re.compile(r"^osv-scanner version:\s*(\S+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class DeclaredDependency:
    ecosystem: str
    name: str
    manifest_source: str
    exact_pin: bool
    scanner_requirement: str | None = None


def parse_scanner_version(raw_version_output: str) -> str:
    """Extract the installed osv-scanner version from `osv-scanner --version`."""
    match = _VERSION_OUTPUT_RE.search(raw_version_output)
    if match is None:
        raise ValueError("Could not parse osv-scanner version output")
    return match.group(1)


def parse_declared_dependencies(
    artifact_path: str,
    artifact_type: str,
    ecosystem: str,
    content: bytes,
) -> list[DeclaredDependency]:
    """Parse direct dependency declarations from a fetched artifact."""
    parser_map = {
        ("PyPI", "requirements"): _parse_requirements_dependencies,
        ("PyPI", "pyproject"): _parse_pyproject_dependencies,
        ("npm", "package_manifest"): _parse_package_json_dependencies,
    }
    parser = parser_map.get((ecosystem, artifact_type))
    if parser is None:
        return []
    return parser(artifact_path, content)


def normalize_osv_results(
    *,
    manifest: dict,
    raw_output: dict,
    scanner_version: str,
    declared_dependencies: list[DeclaredDependency],
    workspace_root: Path,
) -> dict:
    """Transform raw OSV JSON output into the v1 normalized schema."""
    direct_lookup: dict[tuple[str, str, str], list[DeclaredDependency]] = {}
    fallback_lookup: dict[tuple[str, str], list[DeclaredDependency]] = {}

    for dep in declared_dependencies:
        dep_key = (dep.ecosystem, _canonicalize_name(dep.ecosystem, dep.name), dep.manifest_source)
        direct_lookup.setdefault(dep_key, []).append(dep)
        fallback_lookup.setdefault((dep.ecosystem, _canonicalize_name(dep.ecosystem, dep.name)), []).append(dep)

    manifest_paths = {
        item["path"]
        for item in manifest.get("artifact_fetch", {}).get("artifacts_found", [])
        if isinstance(item, dict) and item.get("path")
    }

    normalized_packages: dict[tuple[str, str, str | None], dict] = {}

    for result in raw_output.get("results", []):
        source_path = result.get("source", {}).get("path", "")
        manifest_source = _map_manifest_source(
            source_path=source_path,
            workspace_root=workspace_root,
            manifest_paths=manifest_paths,
        )
        for package_result in result.get("packages", []):
            package = package_result.get("package", {})
            ecosystem = package.get("ecosystem") or "unknown"
            name = package.get("name") or "unknown"
            version = package.get("version")
            key = (ecosystem, name, version)
            matching_deps = direct_lookup.get(
                (ecosystem, _canonicalize_name(ecosystem, name), manifest_source),
                [],
            )
            if not matching_deps:
                matching_deps = fallback_lookup.get((ecosystem, _canonicalize_name(ecosystem, name)), [])

            dependency_scope = "direct" if matching_deps else (
                "transitive" if manifest_source != "unknown" else "unknown"
            )
            pinned = _is_effectively_pinned(version=version, matching_deps=matching_deps)
            vuln_ids = _collect_vulnerability_ids(package_result)
            vulnerabilities = package_result.get("vulnerabilities", [])
            vuln_status = _determine_vuln_status(
                version=version,
                pinned=pinned,
                vulnerabilities=vulnerabilities,
            )

            candidate = {
                "dependency_scope": dependency_scope,
                "ecosystem": ecosystem,
                "fix_available": _has_fix_available(vulnerabilities),
                "manifest_source": (
                    matching_deps[0].manifest_source
                    if matching_deps
                    else manifest_source
                ),
                "max_severity_bucket": _max_severity_bucket(vulnerabilities),
                "name": name,
                "num_vulns": len(vuln_ids),
                "version": version,
                "vuln_ids": vuln_ids,
                "vuln_status": vuln_status,
            }

            existing = normalized_packages.get(key)
            if existing is None:
                normalized_packages[key] = candidate
            else:
                normalized_packages[key] = _merge_package_records(existing, candidate)

    packages = sorted(
        normalized_packages.values(),
        key=lambda item: (
            str(item["ecosystem"]).lower(),
            str(item["name"]).lower(),
            "" if item["version"] is None else str(item["version"]),
        ),
    )

    resolved_reference = manifest.get("resolved_reference", {})
    return {
        "generated_at_utc": _utc_now_iso(),
        "hf_model_id": manifest["hf_model_id"],
        "model_id": manifest["model_id"],
        "packages": packages,
        "repo_commit_sha": resolved_reference.get("repo_commit_sha", "unknown"),
        "repo_commit_sha_reason": resolved_reference.get("repo_commit_sha_reason", "unknown"),
        "scanner": {
            "name": "osv-scanner",
            "version": scanner_version,
        },
        "schema_version": "1.0",
        "source_repo_url": manifest["source_repo_url"],
    }


def _parse_requirements_dependencies(
    artifact_path: str,
    content: bytes,
) -> list[DeclaredDependency]:
    dependencies: list[DeclaredDependency] = []
    for raw_line in content.decode("utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith(("-", "--")) or "://" in line or line.startswith("git+"):
            continue

        exact_match = _PINNED_REQUIREMENT_RE.match(line)
        if exact_match is not None:
            name = _strip_extras(exact_match.group(1))
            version = exact_match.group(3)
            dependencies.append(
                DeclaredDependency(
                    ecosystem="PyPI",
                    name=name,
                    manifest_source=artifact_path,
                    exact_pin="*" not in version,
                    scanner_requirement=f"{name}=={version}" if "*" not in version else name,
                )
            )
            continue

        name_match = _REQUIREMENT_NAME_RE.match(line.split(";", 1)[0].strip())
        if name_match is None:
            continue
        dependencies.append(
            DeclaredDependency(
                ecosystem="PyPI",
                name=_strip_extras(name_match.group(1)),
                manifest_source=artifact_path,
                exact_pin=False,
                scanner_requirement=_strip_extras(name_match.group(1)),
            )
        )
    return dependencies


def _parse_pyproject_dependencies(
    artifact_path: str,
    content: bytes,
) -> list[DeclaredDependency]:
    data = tomllib.loads(content.decode("utf-8"))
    dependencies: list[DeclaredDependency] = []

    project = data.get("project", {})
    for requirement in project.get("dependencies", []):
        dependencies.extend(_parse_requirements_dependencies(artifact_path, requirement.encode("utf-8")))
    for dep_group in project.get("optional-dependencies", {}).values():
        for requirement in dep_group:
            dependencies.extend(_parse_requirements_dependencies(artifact_path, requirement.encode("utf-8")))

    poetry = data.get("tool", {}).get("poetry", {})
    for section_name in ("dependencies", "dev-dependencies"):
        for name, spec in poetry.get(section_name, {}).items():
            if name.lower() == "python":
                continue
            dependencies.append(
                DeclaredDependency(
                    ecosystem="PyPI",
                    name=name,
                    manifest_source=artifact_path,
                    exact_pin=_is_exact_poetry_spec(spec),
                    scanner_requirement=_poetry_to_requirement(name, spec),
                )
            )
    return dependencies


def _parse_package_json_dependencies(
    artifact_path: str,
    content: bytes,
) -> list[DeclaredDependency]:
    data = json.loads(content.decode("utf-8"))
    dependencies: list[DeclaredDependency] = []
    for section_name in (
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
    ):
        section = data.get(section_name, {})
        if not isinstance(section, dict):
            continue
        for name, spec in section.items():
            dependencies.append(
                DeclaredDependency(
                    ecosystem="npm",
                    name=name,
                    manifest_source=artifact_path,
                    exact_pin=_is_exact_npm_spec(spec),
                    scanner_requirement=None,
                )
            )
    return dependencies


def _strip_extras(package_name: str) -> str:
    return package_name.split("[", 1)[0]


def _is_exact_poetry_spec(spec: object) -> bool:
    if isinstance(spec, str):
        raw = spec.strip()
        if raw.startswith(("^", "~", ">", "<", "*")):
            return False
        if raw.startswith("=="):
            raw = raw[2:].strip()
        return bool(raw) and "*" not in raw and "," not in raw
    if isinstance(spec, dict):
        version = spec.get("version")
        if isinstance(version, str):
            return _is_exact_poetry_spec(version)
    return False


def _is_exact_npm_spec(spec: object) -> bool:
    if not isinstance(spec, str):
        return False
    raw = spec.strip()
    if not raw:
        return False
    if raw.startswith(("^", "~", ">", "<", "*", "workspace:", "file:", "link:", "git+", "github:")):
        return False
    return bool(_SEMVER_EXACT_RE.fullmatch(raw))


def _poetry_to_requirement(name: str, spec: object) -> str:
    if isinstance(spec, str):
        raw = spec.strip()
        if raw.startswith("=="):
            raw = raw[2:].strip()
        if _is_exact_poetry_spec(spec):
            return f"{name}=={raw}"
    elif isinstance(spec, dict):
        version = spec.get("version")
        if isinstance(version, str) and _is_exact_poetry_spec(version):
            cleaned = version[2:].strip() if version.startswith("==") else version.strip()
            return f"{name}=={cleaned}"
    return name


def _canonicalize_name(ecosystem: str, name: str) -> str:
    if ecosystem == "PyPI":
        return _CANONICALIZE_PYPI_RE.sub("-", name).lower()
    return name.lower()


def _map_manifest_source(
    *,
    source_path: str,
    workspace_root: Path,
    manifest_paths: set[str],
) -> str:
    if not source_path:
        return "unknown"
    try:
        relative = Path(source_path).resolve().relative_to(workspace_root.resolve()).as_posix()
        if relative in manifest_paths:
            return relative
    except ValueError:
        pass
    source_path_posix = PurePosixPath(source_path).as_posix()
    for manifest_path in sorted(manifest_paths):
        if source_path_posix.endswith("/" + manifest_path) or source_path_posix == manifest_path:
            return manifest_path
    return "unknown"


def _is_effectively_pinned(
    *,
    version: str | None,
    matching_deps: list[DeclaredDependency],
) -> bool:
    if version in (None, "", "unknown"):
        return False
    if matching_deps:
        return all(dep.exact_pin for dep in matching_deps)
    return True


def _collect_vulnerability_ids(package_result: dict) -> list[str]:
    grouped_ids: set[str] = set()
    seen_group_members: set[str] = set()

    for group in package_result.get("groups", []):
        ids = sorted({str(item) for item in group.get("ids", []) if item})
        if not ids:
            continue
        grouped_ids.add(ids[0])
        seen_group_members.update(ids)

    for vulnerability in package_result.get("vulnerabilities", []):
        vuln_id = vulnerability.get("id")
        if vuln_id and vuln_id not in seen_group_members:
            grouped_ids.add(str(vuln_id))

    return sorted(grouped_ids)


def _determine_vuln_status(
    *,
    version: str | None,
    pinned: bool,
    vulnerabilities: list[dict],
) -> str:
    if version in (None, "", "unknown") or not pinned:
        return "unknown"
    return "vulnerable" if vulnerabilities else "not_vulnerable"


def _max_severity_bucket(vulnerabilities: list[dict]) -> str:
    best = "UNKNOWN"
    for vulnerability in vulnerabilities:
        for candidate in _severity_candidates(vulnerability):
            if _SEVERITY_ORDER[candidate] > _SEVERITY_ORDER[best]:
                best = candidate
    return best


def _severity_candidates(vulnerability: dict) -> list[str]:
    candidates: list[str] = []
    for location in (
        vulnerability.get("database_specific", {}).get("severity"),
        vulnerability.get("ecosystem_specific", {}).get("severity"),
        vulnerability.get("severity"),
    ):
        if isinstance(location, str):
            bucket = _severity_from_text(location)
            if bucket is not None:
                candidates.append(bucket)
        elif isinstance(location, list):
            for item in location:
                score = item.get("score") if isinstance(item, dict) else None
                if isinstance(score, str):
                    bucket = _severity_from_text(score)
                    if bucket is not None:
                        candidates.append(bucket)
    return candidates


def _severity_from_text(raw: str) -> str | None:
    upper = raw.upper()
    for bucket in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if bucket in upper:
            return bucket

    if upper.startswith("CVSS:"):
        return None

    try:
        numeric = float(raw)
    except ValueError:
        return None

    if numeric >= 9.0:
        return "CRITICAL"
    if numeric >= 7.0:
        return "HIGH"
    if numeric >= 4.0:
        return "MEDIUM"
    if numeric > 0:
        return "LOW"
    return "UNKNOWN"


def _has_fix_available(vulnerabilities: list[dict]) -> bool:
    for vulnerability in vulnerabilities:
        database_specific = vulnerability.get("database_specific", {})
        if isinstance(database_specific, dict) and database_specific.get("fixed_version"):
            return True
        for affected in vulnerability.get("affected", []):
            for range_item in affected.get("ranges", []):
                for event in range_item.get("events", []):
                    if isinstance(event, dict) and event.get("fixed"):
                        return True
    return False


def _merge_package_records(existing: dict, candidate: dict) -> dict:
    merged_vuln_ids = sorted(set(existing["vuln_ids"]) | set(candidate["vuln_ids"]))
    merged_scope = _merge_dependency_scope(existing["dependency_scope"], candidate["dependency_scope"])
    merged_status = _merge_vuln_status(existing["vuln_status"], candidate["vuln_status"])
    severity = existing["max_severity_bucket"]
    if _SEVERITY_ORDER[candidate["max_severity_bucket"]] > _SEVERITY_ORDER[severity]:
        severity = candidate["max_severity_bucket"]

    return {
        **existing,
        "dependency_scope": merged_scope,
        "fix_available": existing["fix_available"] or candidate["fix_available"],
        "manifest_source": _prefer_manifest_source(existing["manifest_source"], candidate["manifest_source"]),
        "max_severity_bucket": severity,
        "num_vulns": len(merged_vuln_ids),
        "vuln_ids": merged_vuln_ids,
        "vuln_status": merged_status,
    }


def _merge_dependency_scope(left: str, right: str) -> str:
    if "direct" in (left, right):
        return "direct"
    if "transitive" in (left, right):
        return "transitive"
    return "unknown"


def _merge_vuln_status(left: str, right: str) -> str:
    if "unknown" in (left, right):
        return "unknown"
    if "vulnerable" in (left, right):
        return "vulnerable"
    return "not_vulnerable"


def _prefer_manifest_source(left: str, right: str) -> str:
    if left != "unknown":
        return left
    return right


def _utc_now_iso() -> str:
    from scripts._utils.json_utils import utc_now_iso

    return utc_now_iso()
