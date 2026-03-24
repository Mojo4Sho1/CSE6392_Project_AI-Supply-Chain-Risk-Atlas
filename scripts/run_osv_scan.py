#!/usr/bin/env python3
"""
run_osv_scan.py - M2 OSV scanning and normalization pipeline.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import requests

from scripts._utils.artifact_discovery import fetch_with_retry, parse_github_repo_url
from scripts._utils.csv_parser import CSVContractError, _validate_timestamp
from scripts._utils.json_utils import write_json_atomic
from scripts._utils.osv_scan import (
    DeclaredDependency,
    normalize_osv_results,
    parse_declared_dependencies,
    parse_scanner_version,
)

__version__ = "1.0.0"
SCRIPT_NAME = "run_osv_scan.py"


class ManifestContractError(Exception):
    """Raised when an input manifest violates the expected M1 contract."""


@dataclass(frozen=True)
class FetchedArtifactFile:
    path: str
    ecosystem: str
    artifact_type: str
    content: bytes


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="M2 OSV scanning and normalization pipeline for AI Supply Chain Risk Atlas.",
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Path to a manifests directory or manifest_index.json file",
    )
    parser.add_argument(
        "--output-root",
        required=True,
        metavar="PATH",
        help="Root directory for output files (osv/ will be created here)",
    )
    parser.add_argument(
        "--snapshot-timestamp",
        required=True,
        metavar="TIMESTAMP",
        help="UTC snapshot timestamp in ISO-8601 format with Z suffix",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Process manifests but do not write output files",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    return parser


def load_manifests(input_path: str | Path) -> list[dict]:
    """Load manifest JSON files from a directory or a single file."""
    path = Path(input_path)
    manifest_paths: list[Path]
    if path.is_dir():
        manifest_paths = sorted(path.glob("*/manifest_index.json"))
    elif path.is_file():
        manifest_paths = [path]
    else:
        raise ManifestContractError(f"Input path does not exist: {path}")

    manifests: list[dict] = []
    for manifest_path in manifest_paths:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ManifestContractError(f"Manifest is not valid JSON: {manifest_path}") from exc
        except OSError as exc:
            raise ManifestContractError(f"Cannot read manifest: {manifest_path}") from exc

        _validate_manifest(manifest, manifest_path)
        manifests.append(manifest)

    manifests.sort(
        key=lambda manifest: (
            manifest["hf_model_id"],
            manifest["provenance"]["input_row_number"],
        )
    )
    return manifests


def fetch_manifest_artifacts(
    manifest: dict,
    *,
    session: requests.Session,
    log: logging.Logger,
) -> list[FetchedArtifactFile]:
    """Re-fetch the artifact files recorded in a manifest."""
    owner, repo_name = parse_github_repo_url(manifest["source_repo_url"])
    resolved_reference = manifest["resolved_reference"]
    ref = resolved_reference.get("repo_commit_sha")
    if not ref or ref == "unknown":
        ref = resolved_reference.get("resolved_ref")
    if not ref or ref == "unknown":
        raise ManifestContractError(
            f"Manifest has no fetchable resolved reference for {manifest['model_id']}"
        )

    artifacts: list[FetchedArtifactFile] = []
    for artifact in manifest["artifact_fetch"]["artifacts_found"]:
        artifact_path = artifact["path"]
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{ref}/{artifact_path}"
        response = fetch_with_retry(raw_url, session, log)
        if response is None or response.status_code != 200:
            status = "no_response" if response is None else response.status_code
            raise RuntimeError(
                f"Failed to fetch artifact for {manifest['model_id']}: "
                f"{artifact_path} (HTTP {status})"
            )
        artifacts.append(
            FetchedArtifactFile(
                path=artifact_path,
                ecosystem=artifact["ecosystem"],
                artifact_type=artifact["artifact_type"],
                content=response.content,
            )
        )
    return artifacts


def get_scanner_version() -> str:
    """Return the installed osv-scanner version string."""
    try:
        result = subprocess.run(
            ["osv-scanner", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError("osv-scanner executable not found on PATH") from exc

    if result.returncode != 0:
        raise RuntimeError(f"osv-scanner --version failed with exit code {result.returncode}")
    return parse_scanner_version(result.stdout)


def run_scanner(lockfiles: list[str]) -> tuple[str, dict]:
    """Execute osv-scanner on one or more prepared lockfile paths and return raw JSON."""
    command = ["osv-scanner", "scan", "source"]
    for lockfile in lockfiles:
        command.extend(["-L", lockfile])
    command.extend([
        "--format",
        "json",
        "--all-packages",
        "--verbosity",
        "error",
    ])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError("osv-scanner executable not found on PATH") from exc

    if result.returncode not in (0, 1):
        stderr = result.stderr.strip()
        raise RuntimeError(
            f"osv-scanner failed with exit code {result.returncode}: {stderr or 'no stderr output'}"
        )

    try:
        raw_output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("osv-scanner did not emit valid JSON output") from exc

    return result.stdout, raw_output


def run(args: argparse.Namespace) -> int:
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    log = logging.getLogger(SCRIPT_NAME)

    try:
        _validate_timestamp(args.snapshot_timestamp, "snapshot_timestamp", 0)
    except CSVContractError as exc:
        log.error("Input contract error: %s", exc)
        return 2

    log.info(
        "Starting %s v%s | input=%s | output-root=%s | snapshot=%s | dry-run=%s",
        SCRIPT_NAME,
        __version__,
        args.input,
        args.output_root,
        args.snapshot_timestamp,
        args.dry_run,
    )

    try:
        manifests = load_manifests(args.input)
    except ManifestContractError as exc:
        log.error("Input contract error: %s", exc)
        return 2

    try:
        scanner_version = get_scanner_version()
    except FileNotFoundError as exc:
        log.error("%s", exc)
        return 3
    except Exception as exc:
        log.error("Unable to determine osv-scanner version: %s", exc)
        return 4

    session = requests.Session()
    session.headers.update({
        "User-Agent": f"AI-Supply-Chain-Risk-Atlas/{__version__} ({SCRIPT_NAME})",
        "Accept": "application/vnd.github.v3+json",
    })

    scanned_count = 0
    skipped_count = 0

    try:
        for manifest in manifests:
            model_id = manifest["model_id"]
            if not manifest["eligibility"]["eligible"]:
                skipped_count += 1
                log.info(
                    "Skipping ineligible manifest: %s (%s)",
                    manifest["hf_model_id"],
                    manifest["eligibility"]["reason_code"],
                )
                continue

            log.info("Scanning eligible manifest: %s -> %s", manifest["hf_model_id"], model_id)
            artifact_files = fetch_manifest_artifacts(manifest, session=session, log=log)
            declared_dependencies: list[DeclaredDependency] = []

            with tempfile.TemporaryDirectory(prefix=f"osv-{model_id}-") as tmp_dir_name:
                workspace_dir = Path(tmp_dir_name)
                for artifact_file in artifact_files:
                    artifact_dependencies = parse_declared_dependencies(
                        artifact_path=artifact_file.path,
                        artifact_type=artifact_file.artifact_type,
                        ecosystem=artifact_file.ecosystem,
                        content=artifact_file.content,
                    )
                    declared_dependencies.extend(artifact_dependencies)
                    _materialize_scannable_artifact(
                        workspace_dir=workspace_dir,
                        artifact_file=artifact_file,
                        declared_dependencies=artifact_dependencies,
                    )

                lockfiles = _collect_scannable_lockfiles(workspace_dir)
                if lockfiles:
                    raw_text, raw_output = run_scanner(lockfiles)
                else:
                    log.info(
                        "No scanable lockfiles prepared for %s; emitting empty OSV result set",
                        model_id,
                    )
                    raw_text = '{\n  "results": []\n}\n'
                    raw_output = {"results": []}
                normalized = normalize_osv_results(
                    manifest=manifest,
                    raw_output=raw_output,
                    scanner_version=scanner_version,
                    declared_dependencies=declared_dependencies,
                    workspace_root=workspace_dir,
                )

                if not args.dry_run:
                    raw_path = Path(args.output_root) / "osv" / model_id / "raw.json"
                    normalized_path = Path(args.output_root) / "osv" / model_id / "normalized.json"
                    _write_text_atomic(raw_path, raw_text)
                    write_json_atomic(normalized_path, normalized)

            scanned_count += 1

    except ManifestContractError as exc:
        log.error("Input contract error: %s", exc)
        return 2
    except FileNotFoundError as exc:
        log.error("%s", exc)
        return 3
    except Exception as exc:
        log.exception("Fatal error during OSV scanning: %s", exc)
        return 4

    log.info(
        "Done. scanned=%d skipped=%d total=%d%s",
        scanned_count,
        skipped_count,
        len(manifests),
        " [DRY RUN - no files written]" if args.dry_run else "",
    )
    return 0


def _validate_manifest(manifest: dict, manifest_path: Path) -> None:
    required_top_level = [
        "artifact_fetch",
        "eligibility",
        "hf_model_id",
        "model_id",
        "provenance",
        "resolved_reference",
        "source_repo_url",
    ]
    for field in required_top_level:
        if field not in manifest:
            raise ManifestContractError(f"Manifest missing required field '{field}': {manifest_path}")

    artifacts_found = manifest["artifact_fetch"].get("artifacts_found")
    if not isinstance(artifacts_found, list):
        raise ManifestContractError(f"Manifest has invalid artifact list: {manifest_path}")

    eligibility = manifest["eligibility"]
    if "eligible" not in eligibility or "reason_code" not in eligibility:
        raise ManifestContractError(f"Manifest has invalid eligibility block: {manifest_path}")

    if "input_row_number" not in manifest["provenance"]:
        raise ManifestContractError(f"Manifest missing provenance.input_row_number: {manifest_path}")

    resolved_reference = manifest["resolved_reference"]
    if "repo_commit_sha_reason" not in resolved_reference:
        raise ManifestContractError(f"Manifest missing resolved_reference.repo_commit_sha_reason: {manifest_path}")

    for index, artifact in enumerate(artifacts_found, start=1):
        for field in ("artifact_type", "ecosystem", "path"):
            if field not in artifact:
                raise ManifestContractError(
                    f"Manifest artifact #{index} missing '{field}': {manifest_path}"
                )


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def _materialize_scannable_artifact(
    *,
    workspace_dir: Path,
    artifact_file: FetchedArtifactFile,
    declared_dependencies: list[DeclaredDependency],
) -> None:
    if artifact_file.artifact_type == "requirements":
        target_path = workspace_dir / artifact_file.path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(artifact_file.content)
        return

    if artifact_file.ecosystem == "PyPI" and artifact_file.artifact_type == "pyproject":
        target_path = workspace_dir / Path(artifact_file.path).parent / "_synthetic_requirements" / "requirements.txt"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        requirement_lines = [
            dep.scanner_requirement
            for dep in declared_dependencies
            if dep.ecosystem == "PyPI" and dep.scanner_requirement
        ]
        if requirement_lines:
            target_path.write_text("\n".join(requirement_lines) + "\n", encoding="utf-8")
        return


def _collect_scannable_lockfiles(workspace_dir: Path) -> list[str]:
    try:
        return sorted(
            str(path)
            for path in workspace_dir.rglob("*")
            if path.is_file() and path.name in (
                "requirements.txt",
                "package-lock.json",
                "yarn.lock",
                "pnpm-lock.yaml",
            )
        )
    except OSError as exc:
        raise RuntimeError(f"Could not enumerate scanner inputs under {workspace_dir}") from exc


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
