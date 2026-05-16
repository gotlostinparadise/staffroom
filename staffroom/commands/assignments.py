"""Assignment CLI command handlers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from staffroom.storage.assignments import (
    add_assignment_evidence,
    add_assignment_note,
    activate_assignment,
    assign_assignment,
    close_assignment,
    create_assignment,
    get_assignment_status,
    list_assignments,
    start_assignment,
    submit_assignment,
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

    list_parser = assignment_subcommands.add_parser("list", help="List assignments")
    list_parser.add_argument("--state", default=None, help="Filter by assignment state")
    list_parser.add_argument("--role", dest="role_id", default=None, help="Filter by role identifier")
    list_parser.add_argument("--agent", dest="agent_id", default=None, help="Filter by assigned agent identifier")
    list_parser.add_argument("--json", action="store_true", help="Emit JSON output")
    list_parser.set_defaults(func=list_assignment_handler)

    assign_parser = assignment_subcommands.add_parser("assign", help="Assign pending work to an agent")
    assign_parser.add_argument("assignment_id")
    assign_parser.add_argument("--agent", required=True, help="Agent identifier")
    assign_parser.add_argument("--supervisor", default="operator", help="Supervisor identifier")
    assign_parser.set_defaults(func=assign_assignment_handler)

    start_parser = assignment_subcommands.add_parser("start", help="Start assigned work as the assigned agent")
    start_parser.add_argument("assignment_id")
    start_parser.add_argument("--agent", required=True, help="Agent identifier")
    start_parser.set_defaults(func=start_assignment_handler)

    activate_parser = assignment_subcommands.add_parser("activate", help="Activate a pending assignment")
    activate_parser.add_argument("assignment_id")
    activate_parser.set_defaults(func=activate_assignment_handler)

    note_parser = assignment_subcommands.add_parser("note", help="Append an agent note to an assignment")
    note_parser.add_argument("assignment_id")
    note_parser.add_argument("--agent", required=True, help="Agent identifier")
    note_parser.add_argument("--text", required=True, help="Note text")
    note_parser.set_defaults(func=note_assignment_handler)

    evidence_parser = assignment_subcommands.add_parser("evidence", help="Manage assignment evidence")
    evidence_subcommands = evidence_parser.add_subparsers(dest="evidence_action", required=True)
    evidence_add_parser = evidence_subcommands.add_parser("add", help="Add evidence to an assignment")
    evidence_add_parser.add_argument("assignment_id")
    evidence_add_parser.add_argument("--agent", required=True, help="Agent identifier")
    evidence_add_parser.add_argument("--kind", required=True, help="Evidence kind")
    evidence_add_parser.add_argument("--path", required=True, help="Repository-relative evidence path")
    evidence_add_parser.add_argument("--summary", default="", help="Evidence summary")
    evidence_add_parser.set_defaults(func=add_evidence_handler)

    submit_parser = assignment_subcommands.add_parser("submit", help="Submit active work for supervisor review")
    submit_parser.add_argument("assignment_id")
    submit_parser.add_argument("--agent", required=True, help="Agent identifier")
    submit_parser.add_argument("--notes", required=True, help="Submission notes")
    submit_parser.set_defaults(func=submit_assignment_handler)

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


def list_assignment_handler(args: argparse.Namespace) -> int:
    assignments = list_assignments(
        Path(args.root),
        state=args.state,
        role_id=args.role_id,
        agent_id=args.agent_id,
    )
    print(json.dumps(assignments, sort_keys=True))
    return 0


def assign_assignment_handler(args: argparse.Namespace) -> int:
    assignment = assign_assignment(
        Path(args.root),
        args.assignment_id,
        agent_id=args.agent,
        supervisor_id=args.supervisor,
    )
    print(json.dumps(assignment, sort_keys=True))
    return 0


def start_assignment_handler(args: argparse.Namespace) -> int:
    assignment = start_assignment(Path(args.root), args.assignment_id, agent_id=args.agent)
    print(json.dumps(assignment, sort_keys=True))
    return 0


def activate_assignment_handler(args: argparse.Namespace) -> int:
    assignment = activate_assignment(Path(args.root), args.assignment_id)
    print(json.dumps(assignment, sort_keys=True))
    return 0


def note_assignment_handler(args: argparse.Namespace) -> int:
    assignment = add_assignment_note(
        Path(args.root),
        args.assignment_id,
        agent_id=args.agent,
        text=args.text,
    )
    print(json.dumps(assignment, sort_keys=True))
    return 0


def add_evidence_handler(args: argparse.Namespace) -> int:
    assignment = add_assignment_evidence(
        Path(args.root),
        args.assignment_id,
        agent_id=args.agent,
        kind=args.kind,
        path=args.path,
        summary=args.summary,
    )
    print(json.dumps(assignment, sort_keys=True))
    return 0


def submit_assignment_handler(args: argparse.Namespace) -> int:
    assignment = submit_assignment(
        Path(args.root),
        args.assignment_id,
        agent_id=args.agent,
        notes=args.notes,
    )
    print(json.dumps(assignment, sort_keys=True))
    return 0


def status_assignment_handler(args: argparse.Namespace) -> int:
    status = get_assignment_status(Path(args.root), args.assignment_id)
    print(json.dumps(status, sort_keys=True))
    return 0


def close_assignment_handler(args: argparse.Namespace) -> int:
    assignment = close_assignment(
        Path(args.root),
        args.assignment_id,
        result=args.result,
        notes=args.notes,
        closed_by=args.closed_by,
    )
    print(json.dumps(assignment, sort_keys=True))
    return 0
