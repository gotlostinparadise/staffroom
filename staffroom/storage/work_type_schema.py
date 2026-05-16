"""Work type template schema and validation helpers."""

from __future__ import annotations

import re

WORK_TYPE_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")


def validate_work_type_id(work_type_id: str) -> bool:
    return bool(WORK_TYPE_ID_PATTERN.fullmatch(work_type_id))


def validate_string_list(payload: dict, field_name: str) -> None:
    value = payload.get(field_name, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    if any(not item.strip() for item in value):
        raise ValueError(f"{field_name} must contain non-empty strings")


def validate_work_type_payload(payload: dict) -> None:
    required_fields = {
        "work_type_id",
        "name",
        "description",
        "default_expected_outputs",
        "allowed_evidence_kinds",
        "recommended_role_ids",
    }
    missing = required_fields - set(payload)
    if missing:
        raise ValueError(f"work type payload missing required fields: {', '.join(sorted(missing))}")

    work_type_id = payload.get("work_type_id")
    if not isinstance(work_type_id, str) or not validate_work_type_id(work_type_id):
        raise ValueError(f"invalid work_type_id: {work_type_id}")

    if not isinstance(payload.get("name"), str) or not payload["name"].strip():
        raise ValueError("name must be a non-empty string")

    if not isinstance(payload.get("description"), str):
        raise ValueError("description must be a string")

    for field_name in ("default_expected_outputs", "allowed_evidence_kinds", "recommended_role_ids"):
        validate_string_list(payload, field_name)
