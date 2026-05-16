# CIPH Closeout Checklist

Task: general-work-contracts-phase-1
Objective: Generalize Staffroom into a supervised local coordination hub for workers and work types
Manifest: vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json
Root: .

## Prompt-to-Artifact Checklist

- [COVERED] GW01: Add durable worker profile storage and CLI commands for create/list/show.
  - Artifacts: staffroom/storage/workers.py, staffroom/storage/worker_schema.py, staffroom/commands/workers.py, tests/test_workers.py, tests/test_cli_entrypoint.py
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/worker-storage.txt, vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/cli.txt
- [COVERED] GW02: Add durable work type template storage, built-in starter templates, and CLI commands for create/list/show.
  - Artifacts: staffroom/storage/work_types.py, staffroom/storage/work_type_schema.py, staffroom/commands/work_types.py, work_types/coding.json, work_types/research.json, work_types/writing.json, work_types/review.json, work_types/analysis.json, work_types/operations.json, tests/test_work_types.py, tests/test_cli_entrypoint.py
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/work-type-storage.txt, vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/cli.txt
- [COVERED] GW03: Generalize assignment creation with optional Proofline context, work types, expected outputs, acceptance criteria, context refs, and worker assignment compatibility.
  - Artifacts: staffroom/storage/assignment_schema.py, staffroom/storage/assignments.py, staffroom/commands/assignments.py, tests/test_assignment_creation.py, tests/test_proofline_link_validation.py, tests/test_supervisor_protocol.py, tests/test_cli_entrypoint.py
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/assignment-storage.txt, vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/cli.txt
- [COVERED] GW04: Document Staffroom as a general supervised coordination hub and record the design boundary.
  - Artifacts: README.md, docs/plans/2026-05-17-general-work-contracts-phase-1.md
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/readme-smoke.txt
- [COVERED] GW05: Preserve existing behavior and close the run with verifiable Proofline artifacts.
  - Artifacts: staffroom/, tests/, vendor/proofline/runs/general-work-contracts-phase-1/artifacts/status.md, vendor/proofline/runs/general-work-contracts-phase-1/artifacts/closeout.md
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/full-unittest.txt, vendor/proofline/runs/general-work-contracts-phase-1/artifacts/status.md, vendor/proofline/runs/general-work-contracts-phase-1/artifacts/closeout.md
## Required Checks

- [COVERED] manifest-lint
  - Command: python3 vendor/proofline/scripts/lint_manifest.py vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json --root .
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/manifest-lint.txt
- [COVERED] worker-storage
  - Command: python3 -m unittest tests.test_workers
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/worker-storage.txt
- [COVERED] work-type-storage
  - Command: python3 -m unittest tests.test_work_types
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/work-type-storage.txt
- [COVERED] assignment-storage
  - Command: python3 -m unittest tests.test_assignment_creation tests.test_proofline_link_validation tests.test_supervisor_protocol
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/assignment-storage.txt
- [COVERED] cli
  - Command: python3 -m unittest tests.test_cli_entrypoint
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/cli.txt
- [COVERED] full-unittest
  - Command: python3 -m unittest discover tests
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/full-unittest.txt
- [COVERED] readme-smoke
  - Command: python3 - <<'PY'
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
required = ['coordination hub', 'worker create', 'work-type create', 'context_refs', 'assigned_worker_id', 'Proofline']
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f'missing README terms: {missing}')
print('README general work hub terms present')
PY
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/readme-smoke.txt
- [COVERED] run-status-artifact
  - Command: python3 vendor/proofline/scripts/run_status.py vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/general-work-contracts-phase-1/artifacts/status.md
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/run-status.txt
- [COVERED] run-closeout-artifact
  - Command: python3 vendor/proofline/scripts/closeout_check.py vendor/proofline/runs/general-work-contracts-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/general-work-contracts-phase-1/artifacts/closeout.md
  - Evidence: vendor/proofline/runs/general-work-contracts-phase-1/artifacts/checks/closeout-check.txt

## Risks

- Existing compatibility fields and CLI flags must remain readable so older assignments can still be closed.
- Context refs generalize Proofline links without treating Staffroom as a worker runtime.

## Manifest Validation

- COVERED: manifest validation passed.
