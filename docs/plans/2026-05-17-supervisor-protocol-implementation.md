# Supervisor Protocol Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a supervised agent-first assignment protocol to Staffroom while keeping supervisor-owned assignment and closeout authority.

**Architecture:** Extend the existing file-backed assignment store with `assigned` and `review` states, event/evidence arrays, and supervisor/agent metadata. Add CLI commands under the existing `assignment` command group and keep JSON stdout as the machine interface.

**Tech Stack:** Python stdlib, `argparse`, JSON files, `unittest`, vendored Proofline under `vendor/proofline`.

---

### Task 1: Extend Assignment Schema Tests

**Files:**
- Modify: `tests/test_assignment_status.py`
- Create: `tests/test_supervisor_protocol.py`

**Step 1: Write failing tests**

Add tests for:

- `assign_assignment` moves `pending` to `assigned`
- `start_assignment` moves `assigned` to `active`
- wrong agent cannot start assigned work
- `submit_assignment` moves `active` to `review`
- `close_assignment` closes a review assignment
- `list_assignments` filters by state, role, and agent
- `add_assignment_note` appends an event
- `add_assignment_evidence` appends evidence and rejects missing/outside paths

**Step 2: Verify red**

Run:

```bash
python3 -m unittest tests.test_supervisor_protocol
```

Expected: import failures for missing functions.

### Task 2: Implement Storage Protocol

**Files:**
- Modify: `staffroom/storage/assignment_schema.py`
- Modify: `staffroom/storage/assignments.py`

**Step 1: Add schema states**

Add `assigned` and `review` to `ASSIGNMENT_STATUSES`.

**Step 2: Add storage helpers**

Implement:

- `list_assignments(root, state=None, role_id=None, agent_id=None)`
- `assign_assignment(root, assignment_id, agent_id, supervisor_id="operator")`
- `start_assignment(root, assignment_id, agent_id)`
- `add_assignment_note(root, assignment_id, agent_id, text)`
- `add_assignment_evidence(root, assignment_id, agent_id, kind, path, summary="")`
- `submit_assignment(root, assignment_id, agent_id, notes)`

**Step 3: Verify green**

Run:

```bash
python3 -m unittest tests.test_supervisor_protocol
python3 -m unittest discover tests
```

### Task 3: Add CLI Protocol

**Files:**
- Modify: `staffroom/commands/assignments.py`
- Modify: `tests/test_cli_entrypoint.py`

**Step 1: Write failing CLI tests**

Add CLI tests for:

- `assignment assign` prints assigned JSON
- `assignment start` prints active JSON
- `assignment note` prints payload with event
- `assignment evidence add` prints payload with evidence
- `assignment submit` prints review JSON
- `assignment list --state review --json` prints a JSON list

**Step 2: Implement commands**

Add subcommands:

- `assignment list`
- `assignment assign`
- `assignment start`
- `assignment note`
- `assignment evidence add`
- `assignment submit`

All command handlers print `json.dumps(..., sort_keys=True)`.

**Step 3: Verify green**

Run:

```bash
python3 -m unittest tests.test_cli_entrypoint
python3 -m unittest discover tests
```

### Task 4: Update Docs And Proofline Contract

**Files:**
- Modify: `README.md`
- Modify: `vendor/proofline/runs/supervisor-protocol-phase-1/TASK.md`
- Modify: `vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json`

**Step 1: Document supervised usage**

Update README with the supervisor/worker model, new lifecycle, commands, fields, and verification commands.

**Step 2: Fill Proofline contract**

Map every requirement to concrete artifact paths and checks.

**Step 3: Lint contract**

Run:

```bash
python3 vendor/proofline/scripts/lint_manifest.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
```

### Task 5: Closeout

**Files:**
- Generated: `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/status.md`
- Generated: `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/closeout.md`

**Step 1: Run required checks**

```bash
python3 vendor/proofline/scripts/run_checks.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/verify_manifest.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/run_status.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/status.md
python3 vendor/proofline/scripts/closeout_check.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/closeout.md
python3 vendor/proofline/scripts/check_repo.py --root . --runs-dir vendor/proofline/runs
```

**Step 2: Commit and push**

Commit the README, plan docs, Proofline assets/run, code, tests, and evidence after all checks pass.
