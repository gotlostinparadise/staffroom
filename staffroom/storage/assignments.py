"""Assignment persistence and state transitions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import uuid

from staffroom.integrations.proofline import validate_proofline_link
from staffroom.storage.assignment_schema import (
    ASSIGNMENT_RESULTS,
    ASSIGNMENT_STATUSES,
    validate_assignment_id,
    validate_assignment_payload,
)
from staffroom.storage.roles import RoleNotFoundError, role_exists


class AssignmentError(ValueError):
    """Base exception for assignment operations."""


class AssignmentNotFoundError(AssignmentError):
    """Raised when the assignment cannot be located."""


class AssignmentValidationError(AssignmentError):
    """Raised when assignment data is invalid."""


class AssignmentStateError(AssignmentError):
    """Raised when an invalid assignment transition is requested."""


def assignment_path(root: Path | str, state: str, assignment_id: str) -> Path:
    return Path(root) / "assignments" / state / f"{assignment_id}.json"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _states() -> tuple[str, ...]:
    return tuple(sorted(ASSIGNMENT_STATUSES))


def _find_assignment(root: Path | str, assignment_id: str) -> tuple[str, Path]:
    root_path = Path(root)
    if not validate_assignment_id(assignment_id):
        raise AssignmentValidationError(
            f"Invalid assignment_id '{assignment_id}'. Must match ^asg_[a-z0-9]{8}$"
        )

    for state in _states():
        candidate = assignment_path(root_path, state, assignment_id)
        if candidate.exists():
            return state, candidate
    raise AssignmentNotFoundError(f"Assignment not found: {assignment_id}")


def create_assignment(
    root: Path | str,
    role_id: str,
    title: str,
    proofline_link: dict,
    assignment_id: str | None = None,
) -> dict:
    root_path = Path(root)
    if not role_exists(root_path, role_id):
        raise RoleNotFoundError(f"Role not found: {role_id}")

    if not proofline_link:
        raise AssignmentValidationError("proofline_link is required")
    try:
        proofline_link = validate_proofline_link(proofline_link, root_path)
    except ValueError as exc:
        raise AssignmentValidationError(str(exc)) from exc

    generated = assignment_id or f"asg_{uuid.uuid4().hex[:8]}"
    if not validate_assignment_id(generated):
        raise AssignmentValidationError(
            f"assignment_id '{generated}' is invalid; expected ^asg_[a-z0-9]{{8}}$"
        )

    payload = {
        "assignment_id": generated,
        "role_id": role_id,
        "title": title,
        "status": "pending",
        "created_at_utc": _utc_timestamp(),
        "proofline_link": proofline_link,
    }

    try:
        validate_assignment_payload(payload)
    except ValueError as exc:
        raise AssignmentValidationError(str(exc)) from exc

    destination = assignment_path(root_path, "pending", generated)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise AssignmentError(f"Assignment already exists: {generated}")

    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def load_assignment(root: Path | str, assignment_id: str) -> tuple[str, dict]:
    state, path = _find_assignment(root, assignment_id)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return state, raw


def get_assignment_status(root: Path | str, assignment_id: str) -> dict:
    _, payload = load_assignment(root, assignment_id)
    return payload


def activate_assignment(root: Path | str, assignment_id: str) -> dict:
    root_path = Path(root)
    state, path = _find_assignment(root_path, assignment_id)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if state != "pending":
        raise AssignmentStateError(f"Can only activate pending assignments. Current status: {state}")

    payload["status"] = "active"
    target = assignment_path(root_path, "active", assignment_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    path.unlink()
    return payload


def close_assignment(
    root: Path | str,
    assignment_id: str,
    *,
    result: str,
    notes: str,
    closed_by: str = "system",
) -> dict:
    root_path = Path(root)
    if not isinstance(result, str) or result not in ASSIGNMENT_RESULTS:
        raise AssignmentValidationError(f"Invalid result '{result}'.")
    if not isinstance(notes, str) or not notes.strip():
        raise AssignmentValidationError("notes must be a non-empty string")
    if not isinstance(closed_by, str) or not closed_by.strip():
        raise AssignmentValidationError("closed_by must be a non-empty string")

    state, path = _find_assignment(root_path, assignment_id)
    if state == "closed":
        raise AssignmentStateError(f"Assignment already closed: {assignment_id}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["status"] = "closed"
    payload["closed_at_utc"] = _utc_timestamp()
    payload["result"] = result
    payload["notes"] = notes
    payload["closed_by"] = closed_by

    target = assignment_path(root_path, "closed", assignment_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    path.unlink()
    return payload
