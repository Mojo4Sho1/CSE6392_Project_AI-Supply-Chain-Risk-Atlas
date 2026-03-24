#!/usr/bin/env python3
"""
generate_atlas_reports.py - M4 report generation pipeline.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts._utils.csv_parser import CSVContractError, _validate_timestamp
from scripts._utils.report_build import (
    ReportContractError,
    build_summary_payload,
    generate_figures,
    load_graph,
    write_summary_csv,
    write_summary_json,
)

__version__ = "1.0.0"
SCRIPT_NAME = "generate_atlas_reports.py"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="M4 reporting pipeline for AI Supply Chain Risk Atlas.",
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Path to graphs/global.graphml or a graphs directory containing it",
    )
    parser.add_argument(
        "--output-root",
        required=True,
        metavar="PATH",
        help="Root directory for output files (reports/ and figures/ will be created here)",
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
        help="Compute metrics and validate inputs but do not write output files",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    return parser


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
        graph, graph_path = load_graph(args.input)
        summary_payload = build_summary_payload(graph=graph, graph_source=graph_path)
    except ReportContractError as exc:
        log.error("Input contract error: %s", exc)
        return 2
    except Exception as exc:
        log.exception("Fatal error during report generation: %s", exc)
        return 4

    if not args.dry_run:
        try:
            summary_json_path = write_summary_json(args.output_root, summary_payload)
            summary_csv_path = write_summary_csv(
                args.output_root,
                summary_payload["per_model_metrics"],
            )
            figure_paths = generate_figures(
                args.output_root,
                summary_payload["reused_vulnerable_packages"],
            )
        except Exception as exc:
            log.exception("Fatal error while writing report outputs: %s", exc)
            return 4
        log.info(
            "Wrote summary_json=%s summary_csv=%s figures=%d",
            summary_json_path,
            summary_csv_path,
            len(figure_paths),
        )

    log.info(
        "Done. models=%d reused_vulnerable_packages=%d%s",
        len(summary_payload["per_model_metrics"]),
        len(summary_payload["reused_vulnerable_packages"]),
        " [DRY RUN - no files written]" if args.dry_run else "",
    )
    return 0


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
