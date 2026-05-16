# CIPH Task

## Objective

Make Staffroom agent-first through a supervised assignment protocol.

## Acceptance Object

The project is acceptable when Staffroom supports a supervised agent workflow in which:

1. A supervisor can list assignments and filter them by state, role, or assigned agent.
2. A supervisor can assign a pending assignment to a specific agent identity.
3. The assigned worker agent can start work, append notes, append evidence, and submit work for review.
4. Assignment evidence is structured, repository-local, and rejects missing, absolute, or outside-repo paths.
5. Submitted assignments enter a `review` state and remain supervisor-closeable.
6. Agents cannot start or submit assignments assigned to a different agent identity.
7. All new command outputs are JSON suitable for agent use.
8. README documents the supervised agent-first model, lifecycle, commands, and verification flow.
9. The run has status and closeout artifacts backed by command evidence.

## Constraints

- Repository rules: keep runtime local, deterministic, and dependency-free.
- Files or areas in scope:
  - `staffroom/`
  - `tests/`
  - `README.md`
  - `docs/plans/`
  - `vendor/proofline/runs/supervisor-protocol-phase-1/`
- Files or areas out of scope:
  - Autonomous work claiming.
  - Leases, heartbeats, schedulers, daemons, network services, or external agent runtimes.
  - External API calls.
- Permissions: local filesystem only.
- Secrets handling: no secrets are required.

## Volatile Facts To Verify

- No external APIs, cloud services, or third-party libraries are used.
- The exact CLI and JSON schemas are repo-owned and defined by this run.

## Deliverables

| ID | Requirement | Artifact paths | Evidence paths |
| --- | --- | --- | --- |
| SP01 | Define the supervised agent-first product design and implementation plan. | `docs/plans/2026-05-17-supervisor-protocol-design.md`, `docs/plans/2026-05-17-supervisor-protocol-implementation.md` | `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/manifest-lint.txt` |
| SP02 | Extend assignment schema and storage with `assigned` and `review` states plus supervisor/agent metadata, events, and evidence. | `assignments/assigned/`, `assignments/review/`, `staffroom/storage/assignment_schema.py`, `staffroom/storage/assignments.py`, `tests/test_supervisor_protocol.py` | `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/supervisor-storage.txt` |
| SP03 | Add agent-facing CLI commands for list, assign, start, note, evidence add, and submit, all with JSON output. | `staffroom/commands/assignments.py`, `tests/test_cli_entrypoint.py` | `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/supervisor-cli.txt` |
| SP04 | Preserve MVP behavior for role creation, assignment creation/status/close, Proofline linkage, and edge cases. | `staffroom/`, `tests/` | `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/full-unittest.txt` |
| SP05 | Document the supervised agent-first workflow and repository verification flow. | `README.md` | `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/readme-smoke.txt` |
| SP06 | Produce run status and closeout artifacts. | `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/status.md`, `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/closeout.md` | `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/status.md`, `vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/closeout.md` |

## Risks And Blockers

- The existing commit lacks the earlier root-level Proofline scripts, so this run uses the vendored Proofline harness under `vendor/proofline`.

## Closeout Commands

```bash
python3 vendor/proofline/scripts/lint_manifest.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/verify_manifest.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
python3 -m unittest discover tests
python3 vendor/proofline/scripts/run_checks.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/run_status.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/status.md
python3 vendor/proofline/scripts/closeout_check.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/closeout.md
python3 vendor/proofline/scripts/check_repo.py --root . --runs-dir vendor/proofline/runs
```
