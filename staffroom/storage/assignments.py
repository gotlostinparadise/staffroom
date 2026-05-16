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
from staffroom.storage.work_type_schema import validate_work_type_id
from staffroom.storage.workers import worker_exists


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


def _load_from_path(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_payload(root: Path, current_path: Path, assignment_id: str, payload: dict) -> dict:
    target = assignment_path(root, payload["status"], assignment_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if target != current_path and current_path.exists():
        current_path.unlink()
    return payload


def _require_non_empty_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AssignmentValidationError(f"{field_name} must be a non-empty string")
    return value


def _ensure_events(payload: dict) -> list[dict]:
    events = payload.setdefault("events", [])
    if not isinstance(events, list):
        raise AssignmentValidationError("events must be a list")
    return events


def _ensure_evidence(payload: dict) -> list[dict]:
    evidence = payload.setdefault("evidence", [])
    if not isinstance(evidence, list):
        raise AssignmentValidationError("evidence must be a list")
    return evidence


def _append_event(payload: dict, event_type: str, actor_id: str, message: str = "") -> None:
    events = _ensure_events(payload)
    events.append(
        {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": event_type,
            "occurred_at_utc": _utc_timestamp(),
            "actor_id": actor_id,
            "message": message,
        }
    )
    payload["updated_at_utc"] = _utc_timestamp()


def _require_assigned_agent(payload: dict, agent_id: str) -> None:
    expected = payload.get("assigned_agent_id")
    if expected != agent_id:
        raise AssignmentStateError(f"Assignment is assigned to {expected}, not {agent_id}")


def _validate_evidence_path(root_path: Path, value: str) -> str:
    path_value = _require_non_empty_string(value, "evidence path")
    candidate = Path(path_value)
    if candidate.is_absolute():
        raise AssignmentValidationError("evidence path must be relative to repo root")

    root_abs = root_path.resolve(strict=False)
    target_abs = (root_path / candidate).resolve(strict=False)
    try:
        target_abs.relative_to(root_abs)
    except ValueError:
        raise AssignmentValidationError(f"evidence path must be inside repo root: {path_value}") from None

    if not target_abs.exists():
        raise AssignmentValidationError(f"evidence path not found: {path_value}")
    return path_value


def _validate_context_path(root_path: Path, value: str, field_name: str) -> str:
    path_value = _require_non_empty_string(value, field_name)
    candidate = Path(path_value)
    if candidate.is_absolute():
        raise AssignmentValidationError(f"{field_name} must be relative to repo root")

    root_abs = root_path.resolve(strict=False)
    target_abs = (root_path / candidate).resolve(strict=False)
    try:
        target_abs.relative_to(root_abs)
    except ValueError:
        raise AssignmentValidationError(f"{field_name} must be inside repo root: {path_value}") from None

    if not target_abs.exists():
        raise AssignmentValidationError(f"{field_name} path not found: {path_value}")
    return path_value


def _normalize_string_list(values: list[str] | None, field_name: str) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise AssignmentValidationError(f"{field_name} must be a list of strings")
    normalized = [item.strip() for item in values]
    if any(not item for item in normalized):
        raise AssignmentValidationError(f"{field_name} must contain non-empty strings")
    return normalized


def _normalize_context_refs(root_path: Path, refs: list[dict] | None) -> list[dict]:
    if refs is None:
        return []
    if not isinstance(refs, list):
        raise AssignmentValidationError("context_refs must be a list")

    normalized: list[dict] = []
    for ref in refs:
        if not isinstance(ref, dict):
            raise AssignmentValidationError("context_refs entries must be objects")
        kind = _require_non_empty_string(ref.get("kind"), "context_refs.kind")
        item: dict = {"kind": kind}

        path_value = ref.get("path")
        value = ref.get("value")
        if path_value is not None:
            item["path"] = _validate_context_path(root_path, path_value, f"context_refs.{kind}.path")
        if value is not None:
            item["value"] = _require_non_empty_string(value, f"context_refs.{kind}.value")

        if "path" not in item and "value" not in item:
            raise AssignmentValidationError("context_refs entries must include path or value")

        if "label" in ref:
            item["label"] = _require_non_empty_string(ref.get("label"), "context_refs.label")

        normalized.append(item)

    return normalized


def _proofline_link_to_context_refs(proofline_link: dict) -> list[dict]:
    refs: list[dict] = []
    if "proofline_run" in proofline_link:
        refs.append({"kind": "proofline_run", "path": proofline_link["proofline_run"]})
    if "child_task" in proofline_link:
        refs.append({"kind": "child_task", "path": proofline_link["child_task"]})
    return refs


def create_assignment(
    root: Path | str,
    role_id: str,
    title: str,
    proofline_link: dict | None = None,
    work_type: str | None = None,
    expected_outputs: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    context_refs: list[dict] | None = None,
    assignment_id: str | None = None,
) -> dict:
    root_path = Path(root)
    if not role_exists(root_path, role_id):
        raise RoleNotFoundError(f"Role not found: {role_id}")

    normalized_proofline_link: dict = {}
    proofline_refs: list[dict] = []
    if proofline_link:
        try:
            normalized_proofline_link = validate_proofline_link(proofline_link, root_path)
        except ValueError as exc:
            raise AssignmentValidationError(str(exc)) from exc
        proofline_refs = _proofline_link_to_context_refs(normalized_proofline_link)

    normalized_context_refs = proofline_refs + _normalize_context_refs(root_path, context_refs)
    normalized_expected_outputs = _normalize_string_list(expected_outputs, "expected_outputs")
    normalized_acceptance_criteria = _normalize_string_list(acceptance_criteria, "acceptance_criteria")
    normalized_work_type = work_type.strip() if isinstance(work_type, str) else None
    if work_type is not None and (not normalized_work_type or not validate_work_type_id(normalized_work_type)):
        raise AssignmentValidationError(f"Invalid work_type '{work_type}'. Must match ^[a-z0-9-]+$")

    if not (
        normalized_proofline_link
        or normalized_context_refs
        or normalized_work_type
        or normalized_expected_outputs
        or normalized_acceptance_criteria
    ):
        raise AssignmentValidationError(
            "assignment contract requires proofline_link, context_refs, work_type, expected_outputs, or acceptance_criteria"
        )

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
        "context_refs": normalized_context_refs,
    }
    if normalized_proofline_link:
        payload["proofline_link"] = normalized_proofline_link
    if normalized_work_type:
        payload["work_type"] = normalized_work_type
    if normalized_expected_outputs:
        payload["expected_outputs"] = normalized_expected_outputs
    if normalized_acceptance_criteria:
        payload["acceptance_criteria"] = normalized_acceptance_criteria

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


def list_assignments(
    root: Path | str,
    *,
    state: str | None = None,
    role_id: str | None = None,
    agent_id: str | None = None,
    worker_id: str | None = None,
) -> list[dict]:
    root_path = Path(root)
    if state is not None and state not in ASSIGNMENT_STATUSES:
        raise AssignmentValidationError(f"Invalid state '{state}'.")

    states = (state,) if state else _states()
    results: list[dict] = []
    for item_state in states:
        state_dir = root_path / "assignments" / item_state
        if not state_dir.exists():
            continue
        for path in sorted(state_dir.glob("*.json")):
            payload = _load_from_path(path)
            if role_id is not None and payload.get("role_id") != role_id:
                continue
            if agent_id is not None and payload.get("assigned_agent_id") != agent_id:
                continue
            if worker_id is not None and payload.get("assigned_worker_id") != worker_id:
                continue
            results.append(payload)

    results.sort(key=lambda item: (item.get("created_at_utc", ""), item.get("assignment_id", "")))
    return results


def assign_assignment(
    root: Path | str,
    assignment_id: str,
    *,
    agent_id: str | None = None,
    worker_id: str | None = None,
    supervisor_id: str = "operator",
) -> dict:
    root_path = Path(root)
    if worker_id is None and agent_id is None:
        raise AssignmentValidationError("worker_id or agent_id is required")

    worker = _require_non_empty_string(worker_id if worker_id is not None else agent_id, "worker_id")
    if worker_id is not None and not worker_exists(root_path, worker):
        raise AssignmentValidationError(f"Worker not found: {worker}")

    supervisor = _require_non_empty_string(supervisor_id, "supervisor_id")
    state, path = _find_assignment(root_path, assignment_id)
    if state != "pending":
        raise AssignmentStateError(f"Can only assign pending assignments. Current status: {state}")

    payload = _load_from_path(path)
    payload["status"] = "assigned"
    payload["assigned_worker_id"] = worker
    payload["assigned_agent_id"] = worker
    payload["assigned_at_utc"] = _utc_timestamp()
    payload["assigned_by"] = supervisor
    _append_event(payload, "assigned", supervisor, f"assigned to {worker}")
    return _write_payload(root_path, path, assignment_id, payload)


def start_assignment(root: Path | str, assignment_id: str, *, agent_id: str) -> dict:
    root_path = Path(root)
    agent = _require_non_empty_string(agent_id, "agent_id")
    state, path = _find_assignment(root_path, assignment_id)
    if state != "assigned":
        raise AssignmentStateError(f"Can only start assigned assignments. Current status: {state}")

    payload = _load_from_path(path)
    _require_assigned_agent(payload, agent)
    payload["status"] = "active"
    payload["started_at_utc"] = _utc_timestamp()
    _append_event(payload, "started", agent, "started work")
    return _write_payload(root_path, path, assignment_id, payload)


def add_assignment_note(root: Path | str, assignment_id: str, *, agent_id: str, text: str) -> dict:
    root_path = Path(root)
    agent = _require_non_empty_string(agent_id, "agent_id")
    note = _require_non_empty_string(text, "text")
    state, path = _find_assignment(root_path, assignment_id)
    if state == "closed":
        raise AssignmentStateError(f"Assignment already closed: {assignment_id}")

    payload = _load_from_path(path)
    _require_assigned_agent(payload, agent)
    _append_event(payload, "note", agent, note)
    return _write_payload(root_path, path, assignment_id, payload)


def add_assignment_evidence(
    root: Path | str,
    assignment_id: str,
    *,
    agent_id: str,
    kind: str,
    path: str,
    summary: str = "",
) -> dict:
    root_path = Path(root)
    agent = _require_non_empty_string(agent_id, "agent_id")
    evidence_kind = _require_non_empty_string(kind, "kind")
    evidence_path = _validate_evidence_path(root_path, path)
    if not isinstance(summary, str):
        raise AssignmentValidationError("summary must be a string")

    state, current_path = _find_assignment(root_path, assignment_id)
    if state not in {"active", "review"}:
        raise AssignmentStateError(f"Can only add evidence to active or review assignments. Current status: {state}")

    payload = _load_from_path(current_path)
    _require_assigned_agent(payload, agent)
    evidence = _ensure_evidence(payload)
    evidence.append(
        {
            "evidence_id": f"ev_{uuid.uuid4().hex[:8]}",
            "kind": evidence_kind,
            "path": evidence_path,
            "added_at_utc": _utc_timestamp(),
            "added_by_agent_id": agent,
            "summary": summary,
        }
    )
    _append_event(payload, "evidence_added", agent, evidence_path)
    return _write_payload(root_path, current_path, assignment_id, payload)


def submit_assignment(root: Path | str, assignment_id: str, *, agent_id: str, notes: str) -> dict:
    root_path = Path(root)
    agent = _require_non_empty_string(agent_id, "agent_id")
    submission_notes = _require_non_empty_string(notes, "notes")
    state, path = _find_assignment(root_path, assignment_id)
    if state != "active":
        raise AssignmentStateError(f"Can only submit active assignments. Current status: {state}")

    payload = _load_from_path(path)
    _require_assigned_agent(payload, agent)
    payload["status"] = "review"
    payload["submitted_at_utc"] = _utc_timestamp()
    payload["submitted_by_agent_id"] = agent
    _append_event(payload, "submitted", agent, submission_notes)
    return _write_payload(root_path, path, assignment_id, payload)


def activate_assignment(root: Path | str, assignment_id: str) -> dict:
    root_path = Path(root)
    state, path = _find_assignment(root_path, assignment_id)
    payload = _load_from_path(path)
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

    payload = _load_from_path(path)
    payload["status"] = "closed"
    payload["closed_at_utc"] = _utc_timestamp()
    payload["result"] = result
    payload["notes"] = notes
    payload["closed_by"] = closed_by
    _append_event(payload, "closed", closed_by, notes)

    target = assignment_path(root_path, "closed", assignment_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    path.unlink()
    return payload
