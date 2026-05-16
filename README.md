# Staffroom

Staffroom is a local, file-backed CLI for supervised agentic staff work.
It is agent-first in its interfaces, but supervisor-first in authority:

- supervisors define roles and assign work
- agents start assigned work, report notes, attach evidence, and submit for review
- supervisors close assignments with final evidence
- every command that returns data emits parseable JSON

Staffroom does not start agents, run schedulers, call external services, or make autonomous assignment decisions.

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

Create an assignment linked to a Proofline run:

```bash
python3 -m staffroom assignment create \
  --role reviewer \
  --title "Review supervisor protocol" \
  --proofline-run vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json
```

Assign it to an agent:

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

Assignments:

```bash
python3 -m staffroom assignment create --role <role_id> --title <text> [--proofline-run <path>] [--child-task <path>]
python3 -m staffroom assignment list [--state <state>] [--role <role_id>] [--agent <agent_id>] [--json]
python3 -m staffroom assignment assign <assignment_id> --agent <agent_id> [--supervisor <id>]
python3 -m staffroom assignment start <assignment_id> --agent <agent_id>
python3 -m staffroom assignment note <assignment_id> --agent <agent_id> --text <text>
python3 -m staffroom assignment evidence add <assignment_id> --agent <agent_id> --kind <kind> --path <path> [--summary <text>]
python3 -m staffroom assignment submit <assignment_id> --agent <agent_id> --notes <text>
python3 -m staffroom assignment status <assignment_id>
python3 -m staffroom assignment close <assignment_id> --result <done|rejected|blocked|error> --notes <text> [--closed-by <id>]
```

The legacy `assignment activate` command still exists for MVP compatibility.

## Proofline Links

Each assignment must link to at least one local Proofline artifact:

- `--proofline-run <path>`: path to a run manifest
- `--child-task <path>`: path to a child task packet

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
- `proofline_link`

Supervised protocol fields are added as work progresses:

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
