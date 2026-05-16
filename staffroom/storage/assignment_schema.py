"""Assignment schema and validation helpers."""

from __future__ import annotations

import re

ASSIGNMENT_ID_PATTERN = re.compile(r"^asg_[a-z0-9]{8}$")
ASSIGNMENT_STATUSES = {"pending", "assigned", "active", "review", "closed"}
ASSIGNMENT_RESULTS = {"done", "rejected", "blocked", "error"}


def validate_assignment_id(assignment_id: str) -> bool:
    return bool(ASSIGNMENT_ID_PATTERN.fullmatch(assignment_id))


def validate_assignment_payload(payload: dict) -> None:
    required_fields = {"assignment_id", "role_id", "title", "status", "created_at_utc", "context_refs"}
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

    if "proofline_link" in payload:
        proofline_link = payload.get("proofline_link")
        if not isinstance(proofline_link, dict):
            raise ValueError("proofline_link must be an object")
        if not proofline_link:
            raise ValueError("proofline_link must include at least one entry")

    context_refs = payload.get("context_refs")
    if not isinstance(context_refs, list):
        raise ValueError("context_refs must be a list")
    for ref in context_refs:
        if not isinstance(ref, dict):
            raise ValueError("context_refs entries must be objects")
        if not isinstance(ref.get("kind"), str) or not ref["kind"].strip():
            raise ValueError("context_refs.kind must be a non-empty string")
        has_path = isinstance(ref.get("path"), str) and bool(ref["path"].strip())
        has_value = isinstance(ref.get("value"), str) and bool(ref["value"].strip())
        if not has_path and not has_value:
            raise ValueError("context_refs entries must include path or value")
        if "label" in ref and (not isinstance(ref["label"], str) or not ref["label"].strip()):
            raise ValueError("context_refs.label must be a non-empty string if provided")

    for field_name in ("expected_outputs", "acceptance_criteria"):
        values = payload.get(field_name, [])
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise ValueError(f"{field_name} must be a list of strings")
        if any(not item.strip() for item in values):
            raise ValueError(f"{field_name} must contain non-empty strings")

    if "work_type" in payload and (not isinstance(payload["work_type"], str) or not payload["work_type"].strip()):
        raise ValueError("work_type must be a non-empty string if provided")

    if "assigned_worker_id" in payload and (
        not isinstance(payload["assigned_worker_id"], str) or not payload["assigned_worker_id"].strip()
    ):
        raise ValueError("assigned_worker_id must be a non-empty string if provided")
