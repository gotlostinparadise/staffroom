CIPH-CHECK-EVIDENCE v1
{"check_name": "readme-smoke", "command": "python3 - <<'PY'\nfrom pathlib import Path\ntext = Path('README.md').read_text(encoding='utf-8')\nrequired = ['coordination hub', 'worker create', 'work-type create', 'context_refs', 'assigned_worker_id', 'Proofline']\nmissing = [item for item in required if item not in text]\nif missing:\n    raise SystemExit(f'missing README terms: {missing}')\nprint('README general work hub terms present')\nPY", "exit_code": 0, "finished_at_utc": "2026-05-16T23:55:14+00:00", "generated_by": "scripts/run_checks.py", "started_at_utc": "2026-05-16T23:55:14+00:00", "status": "PASS"}

## STDOUT

README general work hub terms present

## STDERR

<empty>