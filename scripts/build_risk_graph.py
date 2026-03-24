#!/usr/bin/env python3
"""
build_risk_graph.py - M3 global graph construction pipeline.
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
from scripts._utils.graph_build import (
    GraphContractError,
    build_global_graph,
    load_normalized_outputs,
    validate_graph,
    write_graphml_atomic,
)

__version__ = "1.0.0"
SCRIPT_NAME = "build_risk_graph.py"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="M3 graph construction pipeline for AI Supply Chain Risk Atlas.",
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Path to an osv directory or normalized.json file",
    )
    parser.add_argument(
        "--output-root",
        required=True,
        metavar="PATH",
        help="Root directory for output files (graphs/ will be created here)",
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
        help="Build and validate the graph but do not write output files",
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
        normalized_records = load_normalized_outputs(args.input)
        graph = build_global_graph(
            normalized_records=normalized_records,
            snapshot_timestamp=args.snapshot_timestamp,
        )
        validate_graph(graph)
    except GraphContractError as exc:
        log.error("Input contract error: %s", exc)
        return 2
    except Exception as exc:
        log.exception("Fatal error during graph build: %s", exc)
        return 4

    model_count = sum(
        1 for _, attrs in graph.nodes(data=True) if attrs.get("node_type") == "Model"
    )
    package_count = sum(
        1 for _, attrs in graph.nodes(data=True) if attrs.get("node_type") == "Package"
    )

    if not args.dry_run:
        output_path = Path(args.output_root) / "graphs" / "global.graphml"
        try:
            import networkx as nx

            write_graphml_atomic(graph, output_path)
            nx.read_graphml(output_path)
        except Exception as exc:
            log.exception("Fatal error while writing/loading GraphML: %s", exc)
            return 4

    log.info(
        "Done. models=%d packages=%d edges=%d%s",
        model_count,
        package_count,
        graph.number_of_edges(),
        " [DRY RUN - no files written]" if args.dry_run else "",
    )
    return 0


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
