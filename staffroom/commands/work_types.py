"""Work type CLI command handlers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from staffroom.storage.work_types import create_work_type, get_work_type, list_work_types


def register_work_type_commands(subparsers: argparse._SubParsersAction) -> None:
    work_type_parser = subparsers.add_parser("work-type", help="Manage work type templates")
    work_type_subcommands = work_type_parser.add_subparsers(dest="action", required=True)

    create_parser = work_type_subcommands.add_parser("create", help="Create a work type template")
    create_parser.add_argument("work_type_id", help="Work type slug")
    create_parser.add_argument("--name", required=True, help="Work type name")
    create_parser.add_argument("--description", default="", help="Work type description")
    create_parser.add_argument(
        "--expected-output",
        action="append",
        default=[],
        dest="default_expected_outputs",
        help="Default expected output (can be repeated)",
    )
    create_parser.add_argument(
        "--evidence-kind",
        action="append",
        default=[],
        dest="allowed_evidence_kinds",
        help="Allowed evidence kind suggestion (can be repeated)",
    )
    create_parser.add_argument(
        "--recommended-role",
        action="append",
        default=[],
        dest="recommended_role_ids",
        help="Recommended role id (can be repeated)",
    )
    create_parser.set_defaults(func=create_work_type_handler)

    list_parser = work_type_subcommands.add_parser("list", help="List work type templates")
    list_parser.set_defaults(func=list_work_type_handler)

    show_parser = work_type_subcommands.add_parser("show", help="Show a work type template")
    show_parser.add_argument("work_type_id")
    show_parser.set_defaults(func=show_work_type_handler)


def create_work_type_handler(args: argparse.Namespace) -> int:
    payload = create_work_type(
        Path(args.root),
        args.work_type_id,
        name=args.name,
        description=args.description,
        default_expected_outputs=args.default_expected_outputs,
        allowed_evidence_kinds=args.allowed_evidence_kinds,
        recommended_role_ids=args.recommended_role_ids,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


def list_work_type_handler(args: argparse.Namespace) -> int:
    payload = list_work_types(Path(args.root))
    print(json.dumps(payload, sort_keys=True))
    return 0


def show_work_type_handler(args: argparse.Namespace) -> int:
    payload = get_work_type(Path(args.root), args.work_type_id)
    print(json.dumps(payload, sort_keys=True))
    return 0
