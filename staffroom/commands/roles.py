"""Role CLI command handlers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from staffroom.storage.roles import RoleError, create_role


def register_role_commands(subparsers: argparse._SubParsersAction) -> None:
    role_parser = subparsers.add_parser("role", help="Manage staff roles")
    role_subcommands = role_parser.add_subparsers(dest="action", required=True)

    create_parser = role_subcommands.add_parser("create", help="Create a new staff role")
    create_parser.add_argument("role_id", help="Role slug (lowercase letters, numbers, and hyphens)")
    create_parser.add_argument("--name", required=True, help="Role name")
    create_parser.add_argument("--description", default="", help="Role description")
    create_parser.add_argument(
        "--capability",
        action="append",
        default=[],
        dest="capabilities",
        help="Role capability (can be repeated)",
    )
    create_parser.set_defaults(func=create_role_handler)


def create_role_handler(args: argparse.Namespace) -> int:
    try:
        payload = create_role(
            Path(args.root),
            args.role_id,
            name=args.name,
            description=args.description,
            capabilities=args.capabilities,
        )
        print(json.dumps(payload, sort_keys=True))
    except RoleError as exc:
        raise RuntimeError(str(exc))
    return 0
