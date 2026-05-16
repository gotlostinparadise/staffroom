from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.assignments import activate_assignment, create_assignment, get_assignment_status
from staffroom.storage.roles import create_role


class TestAssignmentStatus(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        create_role(self.root, role_id="planner", name="Planner")
        child_path = self.root / "runs" / "staffroom-mvp" / "children" / "reviewer" / "CHILD_TASK.md"
        child_path.parent.mkdir(parents=True, exist_ok=True)
        child_path.write_text("# child task", encoding="utf-8")
        run_manifest = self.root / "runs" / "staffroom-mvp" / "MANIFEST.json"
        run_manifest.parent.mkdir(parents=True, exist_ok=True)
        run_manifest.write_text("{}", encoding="utf-8")
        self.assignment = create_assignment(
            self.root,
            role_id="planner",
            title="Status check",
            proofline_link={"child_task": "runs/staffroom-mvp/children/reviewer/CHILD_TASK.md"},
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_assignment_status_changes_with_state(self) -> None:
        pending_status = get_assignment_status(self.root, self.assignment["assignment_id"])
        self.assertEqual(pending_status["status"], "pending")

        activate_assignment(self.root, self.assignment["assignment_id"])
        active_status = get_assignment_status(self.root, self.assignment["assignment_id"])
        self.assertEqual(active_status["status"], "active")


if __name__ == "__main__":
    unittest.main()
