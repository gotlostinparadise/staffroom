"""Role persistence operations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .role_schema import validate_role_id, validate_role_payload


class RoleError(ValueError):
    """Base exception for role operations."""


class RoleNotFoundError(RoleError):
    """Raised when a role record cannot be located."""


class RoleValidationError(RoleError):
    """Raised when role payload is invalid."""


def role_path(root: Path | str, role_id: str) -> Path:
    return Path(root) / "staff" / f"{role_id}.json"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_role(
    root: Path | str,
    role_id: str,
    name: str,
    description: str = "",
    capabilities: list[str] | None = None,
) -> dict:
    if not validate_role_id(role_id):
        raise RoleValidationError(f"Invalid role_id '{role_id}'. Must match ^[a-z0-9-]+$")

    root_path = Path(root)
    payload: dict = {
        "role_id": role_id,
        "name": name,
        "description": description,
        "capabilities": capabilities or [],
        "created_at_utc": _utc_timestamp(),
    }

    try:
        validate_role_payload(payload)
    except ValueError as exc:
        raise RoleValidationError(str(exc)) from exc

    destination = role_path(root_path, role_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise RoleError(f"Role already exists: {role_id}")

    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def get_role(root: Path | str, role_id: str) -> dict:
    destination = role_path(Path(root), role_id)
    if not destination.exists():
        raise RoleNotFoundError(f"Role not found: {role_id}")
    return json.loads(destination.read_text(encoding="utf-8"))


def role_exists(root: Path | str, role_id: str) -> bool:
    return role_path(root, role_id).exists()

