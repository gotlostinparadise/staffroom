"""Assignment CLI command handlers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from staffroom.storage.assignments import (
    activate_assignment,
    close_assignment,
    create_assignment,
    get_assignment_status,
)


def register_assignment_commands(subparsers: argparse._SubParsersAction) -> None:
    assignment_parser = subparsers.add_parser("assignment", help="Manage assignments")
    assignment_subcommands = assignment_parser.add_subparsers(dest="action", required=True)

    create_parser = assignment_subcommands.add_parser("create", help="Create an assignment")
    create_parser.add_argument("--role", required=True, help="Role identifier")
    create_parser.add_argument("--title", required=True, help="Human-readable assignment title")
    create_parser.add_argument("--proofline-run", dest="proofline_run", default=None, help="Path to a Proofline run")
    create_parser.add_argument("--child-task", dest="child_task", default=None, help="Path to a child task packet")
    create_parser.set_defaults(func=create_assignment_handler)

    activate_parser = assignment_subcommands.add_parser("activate", help="Activate a pending assignment")
    activate_parser.add_argument("assignment_id")
    activate_parser.set_defaults(func=activate_assignment_handler)

    status_parser = assignment_subcommands.add_parser("status", help="Show assignment status")
    status_parser.add_argument("assignment_id")
    status_parser.set_defaults(func=status_assignment_handler)

    close_parser = assignment_subcommands.add_parser("close", help="Close an assignment")
    close_parser.add_argument("assignment_id")
    close_parser.add_argument(
        "--result",
        required=True,
        choices=["done", "rejected", "blocked", "error"],
        help="Close result",
    )
    close_parser.add_argument("--notes", required=True, help="Close notes/evidence")
    close_parser.add_argument("--closed-by", default="operator", help="Identifier for closer")
    close_parser.set_defaults(func=close_assignment_handler)


def create_assignment_handler(args: argparse.Namespace) -> int:
    proofline_link = {}
    if args.proofline_run:
        proofline_link["proofline_run"] = args.proofline_run
    if args.child_task:
        proofline_link["child_task"] = args.child_task

    assignment = create_assignment(
        Path(args.root),
        role_id=args.role,
        title=args.title,
        proofline_link=proofline_link,
    )
    print(json.dumps(assignment, sort_keys=True))
    return 0


def activate_assignment_handler(args: argparse.Namespace) -> int:
    activate_assignment(Path(args.root), args.assignment_id)
    return 0


def status_assignment_handler(args: argparse.Namespace) -> int:
    status = get_assignment_status(Path(args.root), args.assignment_id)
    print(json.dumps(status, sort_keys=True))
    return 0


def close_assignment_handler(args: argparse.Namespace) -> int:
    close_assignment(
        Path(args.root),
        args.assignment_id,
        result=args.result,
        notes=args.notes,
        closed_by=args.closed_by,
    )
    return 0
