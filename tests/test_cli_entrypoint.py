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

    def test_supervisor_protocol_commands_emit_json(self) -> None:
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

        run_manifest = self.root / "runs" / "staffroom-mvp" / "MANIFEST.json"
        run_manifest.parent.mkdir(parents=True, exist_ok=True)
        run_manifest.write_text("{}", encoding="utf-8")

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
                "--proofline-run",
                "runs/staffroom-mvp/MANIFEST.json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(assignment_result.returncode, 0)
        assignment_id = json.loads(assignment_result.stdout)["assignment_id"]

        assign_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "assignment",
                "assign",
                assignment_id,
                "--agent",
                "agent-reviewer-1",
                "--supervisor",
                "lead",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(assign_result.returncode, 0)
        self.assertEqual(json.loads(assign_result.stdout)["status"], "assigned")

        start_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "assignment",
                "start",
                assignment_id,
                "--agent",
                "agent-reviewer-1",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(start_result.returncode, 0)
        self.assertEqual(json.loads(start_result.stdout)["status"], "active")

        note_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "assignment",
                "note",
                assignment_id,
                "--agent",
                "agent-reviewer-1",
                "--text",
                "working",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(note_result.returncode, 0)
        self.assertEqual(json.loads(note_result.stdout)["events"][-1]["type"], "note")

        evidence_file = self.root / "runs" / "staffroom-mvp" / "artifacts" / "test.txt"
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        evidence_file.write_text("ok", encoding="utf-8")
        evidence_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "assignment",
                "evidence",
                "add",
                assignment_id,
                "--agent",
                "agent-reviewer-1",
                "--kind",
                "test-output",
                "--path",
                "runs/staffroom-mvp/artifacts/test.txt",
                "--summary",
                "test output",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(evidence_result.returncode, 0)
        self.assertEqual(json.loads(evidence_result.stdout)["evidence"][-1]["kind"], "test-output")

        submit_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "assignment",
                "submit",
                assignment_id,
                "--agent",
                "agent-reviewer-1",
                "--notes",
                "ready",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(submit_result.returncode, 0)
        self.assertEqual(json.loads(submit_result.stdout)["status"], "review")

        list_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "assignment",
                "list",
                "--state",
                "review",
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(list_result.returncode, 0)
        listed = json.loads(list_result.stdout)
        self.assertEqual([item["assignment_id"] for item in listed], [assignment_id])


if __name__ == "__main__":
    unittest.main()
