"""Command line interface for Staffroom."""

from __future__ import annotations

import argparse
import sys

from staffroom.commands.assignments import register_assignment_commands
from staffroom.commands.roles import register_role_commands
from staffroom.commands.work_types import register_work_type_commands
from staffroom.commands.workers import register_worker_commands
from staffroom.storage.assignments import AssignmentError, AssignmentNotFoundError, AssignmentStateError
from staffroom.storage.roles import RoleError
from staffroom.storage.work_types import WorkTypeError
from staffroom.storage.workers import WorkerError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="staffroom", description="Staffroom local assignment manager")
    parser.add_argument("--root", default=".", help="Repository root used for data storage")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_role_commands(subparsers)
    register_worker_commands(subparsers)
    register_work_type_commands(subparsers)
    register_assignment_commands(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        handler = getattr(args, "func", None)
        if handler is None:
            parser.print_help()
            return 2

        handler(args)
        return 0
    except (
        RoleError,
        WorkerError,
        WorkTypeError,
        AssignmentError,
        AssignmentStateError,
        AssignmentNotFoundError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
