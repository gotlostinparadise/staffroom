# Supervisor Protocol Phase 1 Design

## Goal

Make Staffroom agent-first without making it autonomous-first. Agents should be able to operate the product through durable, machine-readable commands and files, while a supervisor keeps assignment authority and closeout control.

## Product Boundary

Staffroom remains a local repository tool. It does not start agents, schedule processes, call external APIs, or decide who should do work. It records supervised work contracts and state transitions that humans, supervisor agents, and worker agents can all inspect.

## User Model

- Supervisor: creates roles, creates assignments, assigns assignments to an agent identity, reviews submitted work, and closes assignments.
- Worker agent: reads assigned work, starts work, appends notes/evidence, and submits the assignment for review.
- Staffroom: stores roles, assignments, events, evidence, Proofline links, and JSON command output.
- Proofline: remains the evidence backbone for runs and child task packets.

## Assignment Lifecycle

Phase 1 extends the MVP lifecycle:

```text
pending -> assigned -> active -> review -> closed
```

The existing cancellation path remains:

```text
pending -> closed
assigned -> closed
active -> closed
```

`closed` is terminal. Re-closing a closed assignment must fail.

## Assignment Fields

Existing assignment fields remain valid. New supervised fields are added only when relevant:

- `assigned_agent_id`: non-empty string
- `assigned_at_utc`: ISO-8601 UTC timestamp
- `assigned_by`: supervisor identity
- `started_at_utc`: ISO-8601 UTC timestamp
- `submitted_at_utc`: ISO-8601 UTC timestamp
- `submitted_by_agent_id`: non-empty string
- `updated_at_utc`: ISO-8601 UTC timestamp
- `events`: array of event objects
- `evidence`: array of evidence objects

Event object:

- `event_id`
- `type`
- `occurred_at_utc`
- `actor_id`
- `message`

Evidence object:

- `evidence_id`
- `kind`
- `path`
- `added_at_utc`
- `added_by_agent_id`
- `summary`

Evidence paths must be repository-relative, non-empty, exist on disk, and stay inside the repo root.

## CLI Surface

Existing commands stay available. New commands are:

```bash
python3 -m staffroom assignment list [--state <state>] [--role <role_id>] [--agent <agent_id>]
python3 -m staffroom assignment assign <assignment_id> --agent <agent_id> [--supervisor <id>]
python3 -m staffroom assignment start <assignment_id> --agent <agent_id>
python3 -m staffroom assignment note <assignment_id> --agent <agent_id> --text <text>
python3 -m staffroom assignment evidence add <assignment_id> --agent <agent_id> --kind <kind> --path <path> [--summary <text>]
python3 -m staffroom assignment submit <assignment_id> --agent <agent_id> --notes <text>
```

All commands that return data print JSON to stdout. Errors go to stderr through the existing CLI error path.

## Testing

Use stdlib `unittest`. Tests must cover:

- assignment listing and filters
- supervisor assignment from `pending` to `assigned`
- worker start from `assigned` to `active`
- agent mismatch rejection
- note events
- evidence append and invalid evidence paths
- submit for review
- supervisor close from review
- CLI JSON output for new commands

## Non-Goals

- No autonomous work claiming.
- No leases or heartbeat.
- No external agent runtime integration.
- No network services or background daemons.
