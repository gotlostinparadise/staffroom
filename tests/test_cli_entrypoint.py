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
        self.assertEqual(
            payload["context_refs"],
            [{"kind": "child_task", "path": "runs/staffroom-mvp/children/reviewer/CHILD_TASK.md"}],
        )

    def test_worker_and_work_type_commands_emit_json(self) -> None:
        worker_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "worker",
                "create",
                "agent-reviewer-1",
                "--display-name",
                "Agent Reviewer",
                "--kind",
                "agent",
                "--capability",
                "review",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(worker_result.returncode, 0, worker_result.stderr)
        self.assertEqual(json.loads(worker_result.stdout)["worker_id"], "agent-reviewer-1")

        worker_list = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "worker",
                "list",
                "--kind",
                "agent",
                "--capability",
                "review",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(worker_list.returncode, 0, worker_list.stderr)
        self.assertEqual([item["worker_id"] for item in json.loads(worker_list.stdout)], ["agent-reviewer-1"])

        worker_show = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "worker",
                "show",
                "agent-reviewer-1",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(worker_show.returncode, 0, worker_show.stderr)
        self.assertEqual(json.loads(worker_show.stdout)["display_name"], "Agent Reviewer")

        work_type_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "work-type",
                "create",
                "research",
                "--name",
                "Research",
                "--description",
                "Collect facts",
                "--expected-output",
                "summary",
                "--evidence-kind",
                "url",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(work_type_result.returncode, 0, work_type_result.stderr)
        self.assertEqual(json.loads(work_type_result.stdout)["work_type_id"], "research")

        work_type_list = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "work-type",
                "list",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(work_type_list.returncode, 0, work_type_list.stderr)
        self.assertEqual([item["work_type_id"] for item in json.loads(work_type_list.stdout)], ["research"])

        work_type_show = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "work-type",
                "show",
                "research",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(work_type_show.returncode, 0, work_type_show.stderr)
        self.assertEqual(json.loads(work_type_show.stdout)["name"], "Research")

    def test_assignment_create_general_contract_and_assign_worker(self) -> None:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "role",
                "create",
                "researcher",
                "--name",
                "Researcher",
            ],
            text=True,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "worker",
                "create",
                "human-researcher",
                "--display-name",
                "Human Researcher",
                "--kind",
                "human",
            ],
            text=True,
            capture_output=True,
            check=True,
        )
        brief = self.root / "docs" / "brief.md"
        brief.parent.mkdir(parents=True, exist_ok=True)
        brief.write_text("# brief", encoding="utf-8")

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
                "researcher",
                "--title",
                "Research vendor options",
                "--work-type",
                "research",
                "--expected-output",
                "summary",
                "--acceptance",
                "sources cited",
                "--context-ref",
                "file:docs/brief.md",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(assignment_result.returncode, 0, assignment_result.stderr)
        assignment = json.loads(assignment_result.stdout)
        self.assertEqual(assignment["work_type"], "research")
        self.assertEqual(assignment["expected_outputs"], ["summary"])
        self.assertEqual(assignment["acceptance_criteria"], ["sources cited"])
        self.assertEqual(assignment["context_refs"], [{"kind": "file", "path": "docs/brief.md"}])

        assign_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "staffroom",
                "--root",
                str(self.root),
                "assignment",
                "assign",
                assignment["assignment_id"],
                "--worker",
                "human-researcher",
                "--supervisor",
                "lead",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(assign_result.returncode, 0, assign_result.stderr)
        assigned = json.loads(assign_result.stdout)
        self.assertEqual(assigned["assigned_worker_id"], "human-researcher")

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
