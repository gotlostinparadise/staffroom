"""Worker CLI command handlers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from staffroom.storage.workers import create_worker, get_worker, list_workers


def register_worker_commands(subparsers: argparse._SubParsersAction) -> None:
    worker_parser = subparsers.add_parser("worker", help="Manage worker profiles")
    worker_subcommands = worker_parser.add_subparsers(dest="action", required=True)

    create_parser = worker_subcommands.add_parser("create", help="Create a worker profile")
    create_parser.add_argument("worker_id", help="Worker slug")
    create_parser.add_argument("--display-name", required=True, help="Human-readable worker name")
    create_parser.add_argument("--kind", required=True, choices=["human", "agent", "service", "other"], help="Worker kind")
    create_parser.add_argument(
        "--capability",
        action="append",
        default=[],
        dest="capabilities",
        help="Worker capability (can be repeated)",
    )
    create_parser.set_defaults(func=create_worker_handler)

    list_parser = worker_subcommands.add_parser("list", help="List worker profiles")
    list_parser.add_argument("--kind", default=None, choices=["human", "agent", "service", "other"], help="Filter by worker kind")
    list_parser.add_argument("--capability", default=None, help="Filter by capability")
    list_parser.set_defaults(func=list_worker_handler)

    show_parser = worker_subcommands.add_parser("show", help="Show a worker profile")
    show_parser.add_argument("worker_id")
    show_parser.set_defaults(func=show_worker_handler)


def create_worker_handler(args: argparse.Namespace) -> int:
    payload = create_worker(
        Path(args.root),
        args.worker_id,
        display_name=args.display_name,
        worker_kind=args.kind,
        capabilities=args.capabilities,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


def list_worker_handler(args: argparse.Namespace) -> int:
    payload = list_workers(Path(args.root), worker_kind=args.kind, capability=args.capability)
    print(json.dumps(payload, sort_keys=True))
    return 0


def show_worker_handler(args: argparse.Namespace) -> int:
    payload = get_worker(Path(args.root), args.worker_id)
    print(json.dumps(payload, sort_keys=True))
    return 0
