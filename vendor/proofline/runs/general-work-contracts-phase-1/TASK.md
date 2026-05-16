# CIPH Task

## Objective

Generalize Staffroom into a supervised local coordination hub for workers and work types

## Acceptance Object

Staffroom supports local worker profiles, work type templates, and generalized assignment contracts while preserving existing assignment commands and Proofline compatibility. Acceptance is proven by storage tests, CLI tests, full unittest discovery, README smoke checks, manifest verification, run status, closeout, and the repository Proofline gate.

## Constraints

- Repository rules: keep Staffroom local-first and file-backed; every successful data command emits JSON.
- Files or areas in scope: `staffroom/`, `tests/`, `README.md`, `docs/plans/`, `workers/`, `work_types/`, and this run under `vendor/proofline/runs/`.
- Files or areas out of scope: no worker runtime, process launching, scheduling, leases, retries, external services, or autonomous claiming.
- Permissions: local filesystem changes only.
- Secrets handling: do not print or store secrets; no external API calls are required for this local implementation.

## Volatile Facts To Verify

None. This phase depends on the checked-in Staffroom code and vendored Proofline harness, not external APIs or product configuration.

## Deliverables

| ID | Requirement | Artifact paths | Evidence paths |
| --- | --- | --- | --- |
| GW01 | Add durable worker profile storage and CLI commands for create/list/show. | `staffroom/storage/workers.py`, `staffroom/storage/worker_schema.py`, `staffroom/commands/workers.py`, `tests/test_workers.py`, `tests/test_cli_entrypoint.py` | `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/worker-storage.txt`, `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/cli.txt` |
| GW02 | Add durable work type template storage, built-in starter templates, and CLI commands for create/list/show. | `staffroom/storage/work_types.py`, `staffroom/storage/work_type_schema.py`, `staffroom/commands/work_types.py`, `work_types/*.json`, `tests/test_work_types.py`, `tests/test_cli_entrypoint.py` | `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/work-type-storage.txt`, `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/cli.txt` |
| GW03 | Generalize assignment creation with optional Proofline context, work types, expected outputs, acceptance criteria, context refs, and worker assignment compatibility. | `staffroom/storage/assignment_schema.py`, `staffroom/storage/assignments.py`, `staffroom/commands/assignments.py`, `tests/test_assignment_creation.py`, `tests/test_proofline_link_validation.py`, `tests/test_supervisor_protocol.py`, `tests/test_cli_entrypoint.py` | `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/assignment-storage.txt`, `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/cli.txt` |
| GW04 | Document Staffroom as a general supervised coordination hub and record the design boundary. | `README.md`, `docs/plans/2026-05-17-general-work-contracts-phase-1.md` | `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/readme-smoke.txt` |
| GW05 | Preserve existing behavior and close the run with verifiable Proofline artifacts. | `staffroom/`, `tests/`, `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/status.md`, `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/closeout.md` | `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/full-unittest.txt`, `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/status.md`, `vendor/proofline/runs/general-work-contracts-phase-1/artifacts/closeout.md` |

## Risks And Blockers

- Existing tests assert Proofline links are required. They must be updated to preserve legacy Proofline validation while allowing new generalized contracts.
- The old CLI uses `--agent` throughout lifecycle commands. This phase introduces workers for assignment ownership but keeps runtime/reporting command names compatible.

## Closeout Commands

```bash
python3 vendor/proofline/scripts/lint_manifest.py vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/run_checks.py vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/verify_manifest.py vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json --root .
python3 vendor/proofline/scripts/run_status.py vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/general-work-contracts-phase-1/artifacts/status.md
python3 vendor/proofline/scripts/closeout_check.py vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/general-work-contracts-phase-1/artifacts/closeout.md
python3 vendor/proofline/scripts/check_repo.py --root . --runs-dir vendor/proofline/runs
```
