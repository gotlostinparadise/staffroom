CIPH-CHECK-EVIDENCE v1
{"check_name": "readme-smoke", "command": "python3 - <<'PY'\nfrom pathlib import Path\ntext = Path('README.md').read_text(encoding='utf-8')\nrequired = ['Supervisor', 'assignment assign', 'assignment submit', 'assignment evidence add', 'review', 'vendor/proofline']\nmissing = [item for item in required if item not in text]\nif missing:\n    raise SystemExit(f'missing README terms: {missing}')\nprint('README supervised protocol terms present')\nPY", "exit_code": 0, "finished_at_utc": "2026-05-16T18:20:42+00:00", "generated_by": "scripts/run_checks.py", "started_at_utc": "2026-05-16T18:20:42+00:00", "status": "PASS"}

## STDOUT

README supervised protocol terms present

## STDERR

<empty>