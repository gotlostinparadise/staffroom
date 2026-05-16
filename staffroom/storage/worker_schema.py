"""Worker profile schema and validation helpers."""

from __future__ import annotations

import re

WORKER_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
WORKER_KINDS = {"human", "agent", "service", "other"}


def validate_worker_id(worker_id: str) -> bool:
    return bool(WORKER_ID_PATTERN.fullmatch(worker_id))


def validate_worker_payload(payload: dict) -> None:
    required_fields = {"worker_id", "display_name", "worker_kind", "capabilities", "created_at_utc"}
    missing = required_fields - set(payload)
    if missing:
        raise ValueError(f"worker payload missing required fields: {', '.join(sorted(missing))}")

    worker_id = payload.get("worker_id")
    if not isinstance(worker_id, str) or not validate_worker_id(worker_id):
        raise ValueError(f"invalid worker_id: {worker_id}")

    if not isinstance(payload.get("display_name"), str) or not payload["display_name"].strip():
        raise ValueError("display_name must be a non-empty string")

    worker_kind = payload.get("worker_kind")
    if worker_kind not in WORKER_KINDS:
        raise ValueError(f"worker_kind must be one of: {', '.join(sorted(WORKER_KINDS))}")

    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list) or not all(isinstance(item, str) for item in capabilities):
        raise ValueError("capabilities must be a list of strings")
    if any(not item.strip() for item in capabilities):
        raise ValueError("capabilities must be non-empty strings")
