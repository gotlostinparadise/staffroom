"""Role schema and validation helpers."""

from __future__ import annotations

import re

ROLE_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")


def validate_role_id(role_id: str) -> bool:
    return bool(ROLE_ID_PATTERN.fullmatch(role_id))


def validate_role_payload(payload: dict) -> None:
    required_fields = {"role_id", "name", "created_at_utc"}
    missing = required_fields - set(payload)
    if missing:
        raise ValueError(f"role payload missing required fields: {', '.join(sorted(missing))}")

    role_id = payload.get("role_id")
    if not isinstance(role_id, str) or not validate_role_id(role_id):
        raise ValueError(f"invalid role_id: {role_id}")

    if not isinstance(payload.get("name"), str) or not payload["name"].strip():
        raise ValueError("role name must be a non-empty string")

    if "description" in payload and not isinstance(payload["description"], str):
        raise ValueError("role description must be a string if provided")

    capabilities = payload.get("capabilities")
    if capabilities is not None:
        if not isinstance(capabilities, list) or not all(isinstance(item, str) for item in capabilities):
            raise ValueError("role capabilities must be a list of strings")
        if any(not item.strip() for item in capabilities):
            raise ValueError("role capabilities must be non-empty strings")

