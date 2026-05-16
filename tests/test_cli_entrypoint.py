from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCLIEntrypoint(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_entrypoint_creates_role_and_assignment(self) -> None:
        role_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "role",
                "create",
                "planner",
                "--name",
                "Planner",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(role_result.returncode, 0)
        role_payload = json.loads(role_result.stdout.strip())
        self.assertEqual(role_payload["role_id"], "planner")

        run_manifest = self.root / "runs" / "staffroom-mvp" / "MANIFEST.json"
        run_manifest.parent.mkdir(parents=True, exist_ok=True)
        run_manifest.write_text("{}", encoding="utf-8")

        child_task = self.root / "runs" / "staffroom-mvp" / "children" / "reviewer" / "CHILD_TASK.md"
        child_task.parent.mkdir(parents=True, exist_ok=True)
        child_task.write_text("# child", encoding="utf-8")

        assignment_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "assignment",
                "create",
                "--role",
                "planner",
                "--title",
                "Handle queue",
                "--child-task",
                "runs/staffroom-mvp/children/reviewer/CHILD_TASK.md",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(assignment_result.returncode, 0)
        assignment_payload = json.loads(assignment_result.stdout.strip())
        self.assertEqual(assignment_payload["role_id"], "planner")
        self.assertEqual(assignment_payload["status"], "pending")
        self.assertTrue(assignment_payload["assignment_id"].startswith("asg_"))

        pending = list((self.root / "assignments" / "pending").glob("asg_*.json"))
        self.assertEqual(len(pending), 1)

        payload = json.loads(pending[0].read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pending")
        self.assertEqual(payload["role_id"], "planner")


if __name__ == "__main__":
    unittest.main()
