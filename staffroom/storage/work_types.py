"""Work type template persistence operations."""

from __future__ import annotations

import json
from pathlib import Path

from staffroom.storage.work_type_schema import validate_work_type_id, validate_work_type_payload


class WorkTypeError(ValueError):
    """Base exception for work type operations."""


class WorkTypeNotFoundError(WorkTypeError):
    """Raised when a work type record cannot be located."""


class WorkTypeValidationError(WorkTypeError):
    """Raised when work type payload is invalid."""


def work_type_path(root: Path | str, work_type_id: str) -> Path:
    return Path(root) / "work_types" / f"{work_type_id}.json"


def create_work_type(
    root: Path | str,
    work_type_id: str,
    name: str,
    description: str = "",
    default_expected_outputs: list[str] | None = None,
    allowed_evidence_kinds: list[str] | None = None,
    recommended_role_ids: list[str] | None = None,
) -> dict:
    if not validate_work_type_id(work_type_id):
        raise WorkTypeValidationError(f"Invalid work_type_id '{work_type_id}'. Must match ^[a-z0-9-]+$")

    payload = {
        "work_type_id": work_type_id,
        "name": name,
        "description": description,
        "default_expected_outputs": default_expected_outputs or [],
        "allowed_evidence_kinds": allowed_evidence_kinds or [],
        "recommended_role_ids": recommended_role_ids or [],
    }
    try:
        validate_work_type_payload(payload)
    except ValueError as exc:
        raise WorkTypeValidationError(str(exc)) from exc

    destination = work_type_path(root, work_type_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise WorkTypeError(f"Work type already exists: {work_type_id}")

    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def get_work_type(root: Path | str, work_type_id: str) -> dict:
    if not validate_work_type_id(work_type_id):
        raise WorkTypeValidationError(f"Invalid work_type_id '{work_type_id}'. Must match ^[a-z0-9-]+$")

    path = work_type_path(root, work_type_id)
    if not path.exists():
        raise WorkTypeNotFoundError(f"Work type not found: {work_type_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_work_types(root: Path | str) -> list[dict]:
    work_types_dir = Path(root) / "work_types"
    if not work_types_dir.exists():
        return []

    results = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(work_types_dir.glob("*.json"))]
    results.sort(key=lambda item: item.get("work_type_id", ""))
    return results
