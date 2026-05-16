# CIPH Closeout Checklist

Task: supervisor-protocol-phase-1
Objective: Make Staffroom agent-first through a supervised assignment protocol
Manifest: vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json
Root: .

## Prompt-to-Artifact Checklist

- [COVERED] SP01: Define the supervised agent-first product design and implementation plan.
  - Artifacts: docs/plans/2026-05-17-supervisor-protocol-design.md, docs/plans/2026-05-17-supervisor-protocol-implementation.md
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/manifest-lint.txt
- [COVERED] SP02: Extend assignment schema and storage with assigned/review states plus supervisor/agent metadata, events, and evidence.
  - Artifacts: assignments/assigned/, assignments/review/, staffroom/storage/assignment_schema.py, staffroom/storage/assignments.py, tests/test_supervisor_protocol.py
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/supervisor-storage.txt
- [COVERED] SP03: Add agent-facing CLI commands for list, assign, start, note, evidence add, and submit with JSON output.
  - Artifacts: staffroom/commands/assignments.py, tests/test_cli_entrypoint.py
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/supervisor-cli.txt
- [COVERED] SP04: Preserve MVP role, assignment, Proofline linkage, and close behavior.
  - Artifacts: staffroom/, tests/
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/full-unittest.txt
- [COVERED] SP05: Document the supervised agent-first workflow and verification flow.
  - Artifacts: README.md
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/readme-smoke.txt
- [COVERED] SP06: Produce run status and closeout artifacts.
  - Artifacts: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/status.md, vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/closeout.md
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/status.md, vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/closeout.md
## Required Checks

- [COVERED] manifest-lint
  - Command: python3 vendor/proofline/scripts/lint_manifest.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root .
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/manifest-lint.txt
- [COVERED] supervisor-storage
  - Command: python3 -m unittest tests.test_supervisor_protocol
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/supervisor-storage.txt
- [COVERED] supervisor-cli
  - Command: python3 -m unittest tests.test_cli_entrypoint
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/supervisor-cli.txt
- [COVERED] full-unittest
  - Command: python3 -m unittest discover tests
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/full-unittest.txt
- [COVERED] readme-smoke
  - Command: python3 - <<'PY'
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
required = ['Supervisor', 'assignment assign', 'assignment submit', 'assignment evidence add', 'review', 'vendor/proofline']
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f'missing README terms: {missing}')
print('README supervised protocol terms present')
PY
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/readme-smoke.txt
- [COVERED] run-status-artifact
  - Command: python3 vendor/proofline/scripts/run_status.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/status.md
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/run-status.txt
- [COVERED] run-closeout-artifact
  - Command: python3 vendor/proofline/scripts/closeout_check.py vendor/proofline/runs/supervisor-protocol-phase-1/MANIFEST.json --root . --output vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/closeout.md
  - Evidence: vendor/proofline/runs/supervisor-protocol-phase-1/artifacts/checks/closeout-check.txt

## Risks

- The current root commit does not include the earlier root-level Proofline scripts; this milestone uses vendor/proofline as the durable harness location.

## Manifest Validation

- COVERED: manifest validation passed.
