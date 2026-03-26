#!/usr/bin/env python3
"""
run_dashboard.py - Local dashboard showcase launcher.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts._utils.dashboard_data import DashboardContractError, load_dashboard_state

__version__ = "1.0.0"
SCRIPT_NAME = "run_dashboard.py"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launch the local AI Supply Chain Risk Atlas dashboard.",
    )
    parser.add_argument(
        "--graph",
        default="graphs/global.graphml",
        metavar="PATH",
        help="Path to graphs/global.graphml (default: graphs/global.graphml)",
    )
    parser.add_argument(
        "--summary",
        default="reports/summary.json",
        metavar="PATH",
        help="Path to reports/summary.json (default: reports/summary.json)",
    )
    parser.add_argument(
        "--table",
        default="reports/summary.csv",
        metavar="PATH",
        help="Path to reports/summary.csv (default: reports/summary.csv)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        metavar="HOST",
        help="Host interface to bind locally (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        default=8050,
        metavar="PORT",
        type=int,
        help="Port to bind locally (default: 8050)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    return parser


def run(args: argparse.Namespace, *, serve: bool = True) -> int:
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    log = logging.getLogger(SCRIPT_NAME)

    log.info(
        "Starting %s v%s | graph=%s | summary=%s | table=%s | host=%s | port=%s",
        SCRIPT_NAME,
        __version__,
        args.graph,
        args.summary,
        args.table,
        args.host,
        args.port,
    )

    try:
        state = load_dashboard_state(
            graph_path=args.graph,
            summary_path=args.summary,
            table_path=args.table,
        )
    except DashboardContractError as exc:
        log.error("Input contract error: %s", exc)
        return 2

    try:
        from scripts._utils.dashboard_app import build_app

        app = build_app(state)
    except Exception as exc:
        log.exception("Fatal error while building the dashboard app: %s", exc)
        return 4

    if not serve:
        return 0

    try:
        app.run(host=args.host, port=args.port, debug=False)
    except Exception as exc:
        log.exception("Fatal error while running the dashboard server: %s", exc)
        return 4
    return 0


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
