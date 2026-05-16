from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.assignments import AssignmentValidationError, create_assignment
from staffroom.storage.roles import create_role


class TestProoflineLinkValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        create_role(self.root, role_id="planner", name="Planner")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_reject_empty_assignment_contract(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            create_assignment(
                self.root,
                role_id="planner",
                title="bad link",
                proofline_link={},
            )

    def test_reject_missing_proofline_file(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            create_assignment(
                self.root,
                role_id="planner",
                title="missing run",
                proofline_link={"proofline_run": "runs/nope/MANIFEST.json"},
            )

    def test_reject_absolute_proofline_run_path(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            create_assignment(
                self.root,
                role_id="planner",
                title="abs run",
                proofline_link={"proofline_run": "/tmp/not-a-run.json"},
            )

    def test_reject_parent_traversal_path(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            create_assignment(
                self.root,
                role_id="planner",
                title="outside run",
                proofline_link={"child_task": "../outside/CHILD_TASK.md"},
            )

    def test_accepts_existing_child_task_path(self) -> None:
        child_task = self.root / "runs" / "x" / "children" / "reviewer" / "CHILD_TASK.md"
        child_task.parent.mkdir(parents=True, exist_ok=True)
        child_task.write_text("# child", encoding="utf-8")
        assignment = create_assignment(
            self.root,
            role_id="planner",
            title="good link",
            proofline_link={"child_task": "runs/x/children/reviewer/CHILD_TASK.md"},
        )
        self.assertTrue(assignment["assignment_id"].startswith("asg_"))
        self.assertEqual(
            assignment["context_refs"],
            [{"kind": "child_task", "path": "runs/x/children/reviewer/CHILD_TASK.md"}],
        )

    def test_reject_missing_file_context_ref(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            create_assignment(
                self.root,
                role_id="planner",
                title="missing file",
                proofline_link={},
                context_refs=[{"kind": "file", "path": "docs/missing.md"}],
            )

    def test_reject_outside_context_ref_path(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            create_assignment(
                self.root,
                role_id="planner",
                title="outside file",
                proofline_link={},
                context_refs=[{"kind": "file", "path": "../outside.md"}],
            )


if __name__ == "__main__":
    unittest.main()
