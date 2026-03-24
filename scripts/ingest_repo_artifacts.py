#!/usr/bin/env python3
"""
ingest_repo_artifacts.py — M1 ingestion and eligibility pipeline.

Reads data/models.csv, evaluates eligibility for each model candidate,
and produces manifests/<model_id>/manifest_index.json outputs.

Usage:
    python scripts/ingest_repo_artifacts.py \\
        --input data/models.csv \\
        --output-root . \\
        --snapshot-timestamp 2026-03-23T00:00:00Z

Exit codes:
    0  Success (including expected ineligible candidates)
    2  Input contract violation (bad CSV, missing fields, invalid timestamp)
    3  Missing external dependency
    4  Fatal runtime error
"""

import argparse
import logging
import sys
from pathlib import Path

# Allow running as `python scripts/ingest_repo_artifacts.py` from repo root
# by ensuring the repo root is on sys.path.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import requests

from scripts._utils.artifact_discovery import (
    ArtifactDiscoveryResult,
    discover_artifacts,
)
from scripts._utils.csv_parser import CSVContractError, ModelCandidate, parse_csv
from scripts._utils.eligibility import EligibilityResult, evaluate_eligibility
from scripts._utils.json_utils import utc_now_iso, write_json_atomic
from scripts._utils.model_id import normalize_model_id

__version__ = "1.0.0"
SCRIPT_NAME = "ingest_repo_artifacts.py"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="M1 ingestion and eligibility pipeline for AI Supply Chain Risk Atlas.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Path to the candidate models CSV file (e.g., data/models.csv)",
    )
    parser.add_argument(
        "--output-root",
        required=True,
        metavar="PATH",
        help="Root directory for output files (manifests/ will be created here)",
    )
    parser.add_argument(
        "--snapshot-timestamp",
        required=True,
        metavar="TIMESTAMP",
        help="UTC snapshot timestamp in ISO-8601 format with Z suffix (e.g., 2026-03-23T00:00:00Z)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Process candidates but do not write output files",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    return parser


def build_manifest(
    candidate: ModelCandidate,
    model_id: str,
    discovery: ArtifactDiscoveryResult,
    eligibility: EligibilityResult,
    input_file: str,
    snapshot_timestamp: str,
) -> dict:
    """Assemble the manifest_index.json dict per artifact-schemas.md spec."""
    artifacts_found_list = []
    for a in discovery.artifacts_found:
        artifacts_found_list.append({
            "artifact_type": a.artifact_type,
            "ecosystem": a.ecosystem,
            "parse_status": "parsed",
            "path": a.path,
        })

    return {
        "artifact_fetch": {
            "artifact_parse_failures": discovery.artifact_parse_failures,
            "artifacts_found": artifacts_found_list,
            "mode": "artifact_only",
            "recognized_artifacts": sorted(
                ["requirements.txt", "pyproject.toml", "poetry.lock",
                 "Pipfile", "Pipfile.lock", "package.json",
                 "package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
            ),
        },
        "eligibility": {
            "eligible": eligibility.eligible,
            "reason_code": eligibility.reason_code,
            "reason_detail": eligibility.reason_detail,
        },
        "generated_at_utc": utc_now_iso(),
        "hf_model_id": candidate.hf_model_id,
        "model_id": model_id,
        "provenance": {
            "input_file": input_file,
            "input_row_number": candidate.input_row_number,
            "runner": SCRIPT_NAME,
            "runner_version": __version__,
        },
        "resolved_reference": {
            "repo_commit_sha": discovery.repo_commit_sha,
            "repo_commit_sha_reason": discovery.repo_commit_sha_reason,
            "requested_ref": "default",
            "resolution_strategy": discovery.resolution_strategy,
            "resolved_ref": discovery.resolved_ref,
        },
        "schema_version": "1.0",
        "snapshot_timestamp_utc": snapshot_timestamp,
        "source_repo_url": candidate.source_repo_url,
    }


def run(args: argparse.Namespace) -> int:
    """
    Main logic. Returns exit code integer.
    """
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    log = logging.getLogger(SCRIPT_NAME)

    log.info(
        "Starting %s v%s | input=%s | output-root=%s | snapshot=%s | dry-run=%s",
        SCRIPT_NAME,
        __version__,
        args.input,
        args.output_root,
        args.snapshot_timestamp,
        args.dry_run,
    )

    # Parse CSV — exit 2 on any contract violation
    try:
        candidates = parse_csv(args.input)
    except CSVContractError as e:
        log.error("Input contract error: %s", e)
        return 2

    log.info("Loaded %d candidate(s) from %s", len(candidates), args.input)

    output_root = Path(args.output_root)
    session = requests.Session()
    session.headers.update({
        "User-Agent": f"AI-Supply-Chain-Risk-Atlas/{__version__} ({SCRIPT_NAME})",
        "Accept": "application/vnd.github.v3+json",
    })

    eligible_count = 0
    ineligible_count = 0

    try:
        for candidate in candidates:
            model_id = normalize_model_id(candidate.hf_model_id)
            log.info("Processing: %s → %s", candidate.hf_model_id, model_id)

            discovery = discover_artifacts(
                source_repo_url=candidate.source_repo_url,
                dependency_artifact_url=candidate.dependency_artifact_url,
                dependency_artifact=candidate.dependency_artifact,
                session=session,
                log=log,
            )
            eligibility = evaluate_eligibility(candidate, discovery)

            if eligibility.eligible:
                eligible_count += 1
                log.info(
                    "  [ELIGIBLE] %s — %d artifact(s) found",
                    candidate.hf_model_id,
                    len(discovery.artifacts_found),
                )
            else:
                ineligible_count += 1
                log.info(
                    "  [INELIGIBLE] %s — %s: %s",
                    candidate.hf_model_id,
                    eligibility.reason_code,
                    eligibility.reason_detail,
                )

            manifest = build_manifest(
                candidate=candidate,
                model_id=model_id,
                discovery=discovery,
                eligibility=eligibility,
                input_file=args.input,
                snapshot_timestamp=args.snapshot_timestamp,
            )

            if not args.dry_run:
                manifest_path = output_root / "manifests" / model_id / "manifest_index.json"
                write_json_atomic(manifest_path, manifest)
                log.debug("Wrote manifest: %s", manifest_path)

    except Exception as e:
        log.exception("Fatal error during processing: %s", e)
        return 4

    log.info(
        "Done. eligible=%d ineligible=%d total=%d%s",
        eligible_count,
        ineligible_count,
        len(candidates),
        " [DRY RUN — no files written]" if args.dry_run else "",
    )
    return 0


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
