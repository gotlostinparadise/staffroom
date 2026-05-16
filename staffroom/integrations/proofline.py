"""Proofline-specific helper validation."""

from __future__ import annotations

from pathlib import Path


def validate_proofline_link(value, root: Path | str) -> dict[str, str]:
    root_path = Path(root)
    if not isinstance(value, dict):
        raise ValueError("proofline_link must be an object")

    if not value:
        raise ValueError("proofline_link must include proofline_run and/or child_task")

    allowed_keys = {"proofline_run", "child_task"}
    unknown_keys = set(value) - allowed_keys
    if unknown_keys:
        unknown = ", ".join(sorted(unknown_keys))
        raise ValueError(f"proofline_link contains unknown keys: {unknown}")

    if "proofline_run" not in value and "child_task" not in value:
        raise ValueError("proofline_link must include proofline_run or child_task")

    proofline_run = value.get("proofline_run")
    child_task = value.get("child_task")

    if proofline_run is not None:
        if not isinstance(proofline_run, str) or not proofline_run.strip():
            raise ValueError("proofline_link.proofline_run must be a non-empty string")
        _validate_local_path(root_path, proofline_run, "proofline_run")
        if not (root_path / proofline_run).exists():
            raise ValueError(f"proofline_run path not found: {proofline_run}")

    if child_task is not None:
        if not isinstance(child_task, str) or not child_task.strip():
            raise ValueError("proofline_link.child_task must be a non-empty string")
        _validate_local_path(root_path, child_task, "child_task")
        if not (root_path / child_task).exists():
            raise ValueError(f"child_task path not found: {child_task}")

    return value


def _validate_local_path(root_path: Path, value: str, field_name: str) -> None:
    candidate = Path(value)
    if candidate.is_absolute():
        raise ValueError(f"proofline_link.{field_name} must be relative to repo root")

    root_abs = root_path.resolve(strict=False)
    target_abs = (root_path / value).resolve(strict=False)
    try:
        target_abs.relative_to(root_abs)
    except ValueError:
        raise ValueError(f"proofline_link.{field_name} must be inside repo root: {value}")
