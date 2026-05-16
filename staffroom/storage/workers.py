"""Worker profile persistence operations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from staffroom.storage.worker_schema import WORKER_KINDS, validate_worker_id, validate_worker_payload


class WorkerError(ValueError):
    """Base exception for worker operations."""


class WorkerNotFoundError(WorkerError):
    """Raised when a worker record cannot be located."""


class WorkerValidationError(WorkerError):
    """Raised when worker payload is invalid."""


def worker_path(root: Path | str, worker_id: str) -> Path:
    return Path(root) / "workers" / f"{worker_id}.json"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_worker(
    root: Path | str,
    worker_id: str,
    display_name: str,
    worker_kind: str,
    capabilities: list[str] | None = None,
) -> dict:
    if not validate_worker_id(worker_id):
        raise WorkerValidationError(f"Invalid worker_id '{worker_id}'. Must match ^[a-z0-9-]+$")

    payload = {
        "worker_id": worker_id,
        "display_name": display_name,
        "worker_kind": worker_kind,
        "capabilities": capabilities or [],
        "created_at_utc": _utc_timestamp(),
    }
    try:
        validate_worker_payload(payload)
    except ValueError as exc:
        raise WorkerValidationError(str(exc)) from exc

    destination = worker_path(root, worker_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise WorkerError(f"Worker already exists: {worker_id}")

    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def get_worker(root: Path | str, worker_id: str) -> dict:
    if not validate_worker_id(worker_id):
        raise WorkerValidationError(f"Invalid worker_id '{worker_id}'. Must match ^[a-z0-9-]+$")

    path = worker_path(root, worker_id)
    if not path.exists():
        raise WorkerNotFoundError(f"Worker not found: {worker_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def worker_exists(root: Path | str, worker_id: str) -> bool:
    return validate_worker_id(worker_id) and worker_path(root, worker_id).exists()


def list_workers(
    root: Path | str,
    *,
    worker_kind: str | None = None,
    capability: str | None = None,
) -> list[dict]:
    if worker_kind is not None and worker_kind not in WORKER_KINDS:
        raise WorkerValidationError(f"Invalid worker_kind '{worker_kind}'.")
    if capability is not None and (not isinstance(capability, str) or not capability.strip()):
        raise WorkerValidationError("capability must be a non-empty string")

    workers_dir = Path(root) / "workers"
    if not workers_dir.exists():
        return []

    results: list[dict] = []
    for path in sorted(workers_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if worker_kind is not None and payload.get("worker_kind") != worker_kind:
            continue
        if capability is not None and capability not in payload.get("capabilities", []):
            continue
        results.append(payload)

    results.sort(key=lambda item: item.get("worker_id", ""))
    return results
