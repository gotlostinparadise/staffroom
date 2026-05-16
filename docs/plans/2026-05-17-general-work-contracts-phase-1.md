# General Work Contracts Phase 1

## Direction

Staffroom is a supervised local coordination hub, not a worker runtime. It records who can take work, what type of work is being assigned, what context supports the task, and what evidence closes it.

## Product Boundary

- Keep the existing supervised lifecycle: `pending -> assigned -> active -> review -> closed`.
- Add generic worker profiles for humans, agents, services, and other entities.
- Add work type templates as guidance, not hard routing or execution policy.
- Keep Proofline as optional context and preserve `proofline_link` compatibility.
- Do not add worker launch, leases, scheduling, background polling, retries, or autonomous claiming.

## Data Model

Workers live at `workers/<worker_id>.json` with `worker_id`, `display_name`, `worker_kind`, `capabilities`, and `created_at_utc`.

Work types live at `work_types/<work_type_id>.json` with `work_type_id`, `name`, `description`, `default_expected_outputs`, `allowed_evidence_kinds`, and `recommended_role_ids`.

Assignments now carry `context_refs`, plus optional `work_type`, `expected_outputs`, and `acceptance_criteria`. Proofline run and child task flags normalize into context refs and keep the old `proofline_link` object when supplied.

## Compatibility

`assignment assign --worker` is the preferred assignment command. `assignment assign --agent` remains accepted and writes the same identifier into both `assigned_worker_id` and `assigned_agent_id`.

Existing lifecycle commands still use `--agent` for start, note, evidence, and submit so older supervised-agent workflows keep working.
