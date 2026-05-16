# Staffroom

Staffroom is a local, file-backed coordination hub for supervised work.
It tracks assignments for humans, agents, services, and other workers while keeping supervisors in authority:

- supervisors define roles and assign work
- workers start assigned work, report notes, attach evidence, and submit for review
- supervisors close assignments with final evidence
- every command that returns data emits parseable JSON

Staffroom is a work ledger and evidence hub. It does not start workers, run schedulers, call external services, hold leases, retry work, or make autonomous assignment decisions.

## Requirements

- Python 3.11+ (validated with Python 3.14)
- No runtime or test dependencies outside the Python standard library

## Entrypoint

Run from the repository root:

```bash
python3 -m staffroom [--root <repo-root>] <command>
```

`--root` defaults to `.`.

## Supervised Workflow

```text
pending -> assigned -> active -> review -> closed
```

Cancellation/abort closeout is also allowed from non-closed states:

```text
pending -> closed
assigned -> closed
active -> closed
review -> closed
```

`closed` is terminal.

## Quick Start

Create a role:

```bash
python3 -m staffroom role create reviewer --name "Reviewer" --capability review
```

Create a worker profile:

```bash
python3 -m staffroom worker create agent-reviewer-1 --display-name "Agent Reviewer" --kind agent --capability review
```

Create a work type template:

```bash
python3 -m staffroom work-type create research --name "Research" --expected-output summary --evidence-kind url
```

Create an assignment with a general work contract:

```bash
python3 -m staffroom assignment create \
  --role reviewer \
  --title "Research supervisor protocol options" \
  --work-type research \
  --expected-output summary \
  --acceptance "sources cited" \
  --context-ref file:docs/plans/2026-05-17-supervisor-protocol-design.md
```

Proofline remains optional context for coding or review work:

```bash
python3 -m staffroom assignment create \
  --role reviewer \
  --title "Review supervisor protocol" \
  --proofline-run vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json
```

Assign it to a worker:

```bash
python3 -m staffroom assignment assign asg_12345678 --worker agent-reviewer-1 --supervisor lead
```

The old `--agent` flag remains a compatibility alias and writes the same identifier to `assigned_worker_id` and `assigned_agent_id`:

```bash
python3 -m staffroom assignment assign asg_12345678 --agent agent-reviewer-1 --supervisor lead
```

Agent starts work:

```bash
python3 -m staffroom assignment start asg_12345678 --agent agent-reviewer-1
```

Agent appends a note:

```bash
python3 -m staffroom assignment note asg_12345678 --agent agent-reviewer-1 --text "Started inspection"
```

Agent appends evidence:

```bash
python3 -m staffroom assignment evidence add asg_12345678 \
  --agent agent-reviewer-1 \
  --kind test-output \
  --path vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/full-unittest.txt \
  --summary "Full unittest output"
```

Agent submits for review:

```bash
python3 -m staffroom assignment submit asg_12345678 --agent agent-reviewer-1 --notes "Ready for supervisor review"
```

Supervisor closes:

```bash
python3 -m staffroom assignment close asg_12345678 --result done --notes "Accepted" --closed-by lead
```

## Command Reference

Roles:

```bash
python3 -m staffroom role create <role_id> --name <name> [--description <text>] [--capability <name> ...]
```

Workers:

```bash
python3 -m staffroom worker create <worker_id> --display-name <name> --kind <human|agent|service|other> [--capability <name> ...]
python3 -m staffroom worker list [--kind <human|agent|service|other>] [--capability <name>]
python3 -m staffroom worker show <worker_id>
```

Work types:

```bash
python3 -m staffroom work-type create <work_type_id> --name <name> [--description <text>] [--expected-output <name> ...] [--evidence-kind <kind> ...] [--recommended-role <role_id> ...]
python3 -m staffroom work-type list
python3 -m staffroom work-type show <work_type_id>
```

Assignments:

```bash
python3 -m staffroom assignment create --role <role_id> --title <text> [--work-type <work_type_id>] [--expected-output <name> ...] [--acceptance <text> ...] [--context-ref <kind:value> ...] [--proofline-run <path>] [--child-task <path>]
python3 -m staffroom assignment list [--state <state>] [--role <role_id>] [--worker <worker_id>] [--agent <agent_id>] [--json]
python3 -m staffroom assignment assign <assignment_id> (--worker <worker_id> | --agent <agent_id>) [--supervisor <id>]
python3 -m staffroom assignment start <assignment_id> --agent <agent_id>
python3 -m staffroom assignment note <assignment_id> --agent <agent_id> --text <text>
python3 -m staffroom assignment evidence add <assignment_id> --agent <agent_id> --kind <kind> --path <path> [--summary <text>]
python3 -m staffroom assignment submit <assignment_id> --agent <agent_id> --notes <text>
python3 -m staffroom assignment status <assignment_id>
python3 -m staffroom assignment close <assignment_id> --result <done|rejected|blocked|error> --notes <text> [--closed-by <id>]
```

The legacy `assignment activate` command still exists for MVP compatibility.

## Worker Profiles

Worker profiles are stored under `workers/<worker_id>.json`.

Required fields:

- `worker_id`
- `display_name`
- `worker_kind`
- `capabilities`
- `created_at_utc`

`worker_kind` must be one of:

- `human`
- `agent`
- `service`
- `other`

Worker IDs use lowercase letters, numbers, and hyphens.

## Work Type Templates

Work type templates are stored under `work_types/<work_type_id>.json`.
The repo includes starter templates for `coding`, `research`, `writing`, `review`, `analysis`, and `operations`.

Template fields:

- `work_type_id`
- `name`
- `description`
- `default_expected_outputs`
- `allowed_evidence_kinds`
- `recommended_role_ids`

Templates guide assignment creation. Phase 1 does not require an assignment's `work_type` to already exist, so custom work types remain possible.

## Context Refs

Assignments carry generalized `context_refs` instead of requiring Proofline for every task.
Each context ref is an object with:

- `kind`
- `path` for local repo files
- `value` for non-file references such as URLs or notes
- `label` as optional display text

`--context-ref` accepts `kind:value`. `file`, `proofline_run`, and `child_task` values are stored as local paths; other kinds are stored as values.

Local context paths must be repository-relative, must exist, and must stay inside the repository root.

## Proofline Links

Proofline links are still supported but are no longer mandatory for every assignment:

- `--proofline-run <path>`: path to a run manifest
- `--child-task <path>`: path to a child task packet

These flags are normalized into `context_refs` with `kind` values of `proofline_run` and `child_task`. When present, the legacy `proofline_link` object is also preserved for compatibility.

Rules:

- paths must be repository-relative
- paths must exist
- absolute paths are rejected
- parent traversal outside the repository is rejected

## Data Layout

Roles are stored as:

```text
staff/<role_id>.json
```

Workers are stored as:

```text
workers/<worker_id>.json
```

Work types are stored as:

```text
work_types/<work_type_id>.json
```

Assignments are stored by state:

```text
assignments/pending/<assignment_id>.json
assignments/assigned/<assignment_id>.json
assignments/active/<assignment_id>.json
assignments/review/<assignment_id>.json
assignments/closed/<assignment_id>.json
```

Assignment IDs match:

```text
^asg_[a-z0-9]{8}$
```

## Assignment Fields

Base fields:

- `assignment_id`
- `role_id`
- `title`
- `status`
- `created_at_utc`
- `context_refs`

Optional contract fields:

- `work_type`
- `expected_outputs`
- `acceptance_criteria`
- `proofline_link`

Supervised protocol fields are added as work progresses:

- `assigned_worker_id`
- `assigned_agent_id`
- `assigned_at_utc`
- `assigned_by`
- `started_at_utc`
- `submitted_at_utc`
- `submitted_by_agent_id`
- `updated_at_utc`
- `events`
- `evidence`

Close fields:

- `closed_at_utc`
- `result`
- `closed_by`
- `notes`

## Evidence Rules

`assignment evidence add` accepts repository-local files only.

Evidence fields:

- `evidence_id`
- `kind`
- `path`
- `added_at_utc`
- `added_by_agent_id`
- `summary`

Invalid evidence paths fail before the assignment is modified.

## Verification

Run the full test suite:

```bash
python3 -m unittest discover tests
```

Run the supervised protocol Proofline checks:

```bash
python3 vendor/proofline/scripts/lint_manifest.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/verify_manifest.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/run_checks.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/check_repo.py --root . --runs-dir vendor/proofline/runs
```

## Repository Layout

```text
.
├── assignments/              Assignment artifacts by state
├── docs/plans/               Design and implementation plans
├── staff/                    Role artifacts
├── staffroom/                CLI package
├── tests/                    unittest suite
└── vendor/proofline/         Vendored Proofline harness and run evidence
```
