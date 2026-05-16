"""Assignment schema and validation helpers."""

from __future__ import annotations

import re

ASSIGNMENT_ID_PATTERN = re.compile(r"^asg_[a-z0-9]{8}$")
ASSIGNMENT_STATUSES = {"pending", "active", "closed"}
ASSIGNMENT_RESULTS = {"done", "rejected", "blocked", "error"}


def validate_assignment_id(assignment_id: str) -> bool:
    return bool(ASSIGNMENT_ID_PATTERN.fullmatch(assignment_id))


def validate_assignment_payload(payload: dict) -> None:
    required_fields = {"assignment_id", "role_id", "title", "status", "created_at_utc", "proofline_link"}
    missing = required_fields - set(payload)
    if missing:
        raise ValueError(f"assignment payload missing required fields: {', '.join(sorted(missing))}")

    if not isinstance(payload.get("assignment_id"), str) or not validate_assignment_id(payload["assignment_id"]):
        raise ValueError(f"invalid assignment_id: {payload.get('assignment_id')}")

    if not isinstance(payload.get("role_id"), str) or not payload.get("role_id").strip():
        raise ValueError("role_id must be a non-empty string")

    if not isinstance(payload.get("title"), str) or not payload.get("title").strip():
        raise ValueError("title must be a non-empty string")

    status = payload.get("status")
    if status not in ASSIGNMENT_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(sorted(ASSIGNMENT_STATUSES))}")

    proofline_link = payload.get("proofline_link")
    if not isinstance(proofline_link, dict):
        raise ValueError("proofline_link must be an object")
    if not proofline_link:
        raise ValueError("proofline_link must include at least one entry")

