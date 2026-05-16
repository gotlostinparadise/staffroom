from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.assignments import AssignmentStateError, AssignmentValidationError, close_assignment, create_assignment
from staffroom.storage.roles import create_role


class TestAssignmentClose(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        create_role(self.root, role_id="planner", name="Planner")
        run_manifest = self.root / "runs" / "staffroom-mvp" / "MANIFEST.json"
        run_manifest.parent.mkdir(parents=True, exist_ok=True)
        run_manifest.write_text("{}", encoding="utf-8")
        self.assignment = create_assignment(
            self.root,
            role_id="planner",
            title="Close check",
            proofline_link={"proofline_run": "runs/staffroom-mvp/MANIFEST.json"},
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_close_assignment_records_closed_fields(self) -> None:
        closed = close_assignment(
            self.root,
            self.assignment["assignment_id"],
            result="done",
            notes="completed",
            closed_by="operator",
        )
        self.assertEqual(closed["status"], "closed")
        self.assertEqual(closed["result"], "done")
        self.assertEqual(closed["closed_by"], "operator")
        self.assertEqual(closed["notes"], "completed")
        self.assertIn("closed_at_utc", closed)

    def test_close_already_closed_fails(self) -> None:
        close_assignment(
            self.root,
            self.assignment["assignment_id"],
            result="done",
            notes="first-close",
            closed_by="operator",
        )
        with self.assertRaises(AssignmentStateError):
            close_assignment(
                self.root,
                self.assignment["assignment_id"],
                result="done",
                notes="second-close",
                closed_by="operator",
            )

    def test_invalid_close_result_fails(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            close_assignment(
                self.root,
                self.assignment["assignment_id"],
                result="not-valid",
                notes="oops",
                closed_by="operator",
            )

    def test_invalid_close_evidence_types_fail(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            close_assignment(
                self.root,
                self.assignment["assignment_id"],
                result="done",
                notes=123,
                closed_by="operator",
            )

        with self.assertRaises(AssignmentValidationError):
            close_assignment(
                self.root,
                self.assignment["assignment_id"],
                result="done",
                notes="completed",
                closed_by="",
            )


if __name__ == "__main__":
    unittest.main()
