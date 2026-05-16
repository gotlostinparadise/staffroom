from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.assignments import AssignmentValidationError, create_assignment
from staffroom.storage.roles import create_role


class TestAssignmentCreation(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        create_role(self.root, role_id="planner", name="Planner")
        run_manifest = self.root / "runs" / "staffroom-mvp" / "MANIFEST.json"
        run_manifest.parent.mkdir(parents=True, exist_ok=True)
        run_manifest.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_create_assignment_with_proofline_run(self) -> None:
        assignment = create_assignment(
            self.root,
            role_id="planner",
            title="Coordinate shift schedule",
            proofline_link={"proofline_run": "runs/staffroom-mvp/MANIFEST.json"},
        )
        assignment_path = self.root / "assignments" / "pending" / f"{assignment['assignment_id']}.json"
        self.assertTrue(assignment_path.exists())
        self.assertEqual(assignment["status"], "pending")
        self.assertEqual(
            assignment["context_refs"],
            [{"kind": "proofline_run", "path": "runs/staffroom-mvp/MANIFEST.json"}],
        )

    def test_create_assignment_without_proofline_when_contract_fields_exist(self) -> None:
        assignment = create_assignment(
            self.root,
            role_id="planner",
            title="Summarize sources",
            proofline_link={},
            work_type="research",
            expected_outputs=["source summary"],
            acceptance_criteria=["sources cited"],
        )

        self.assertEqual(assignment["work_type"], "research")
        self.assertEqual(assignment["expected_outputs"], ["source summary"])
        self.assertEqual(assignment["acceptance_criteria"], ["sources cited"])
        self.assertNotIn("proofline_link", assignment)
        self.assertEqual(assignment["context_refs"], [])

    def test_create_assignment_with_file_context_ref(self) -> None:
        brief = self.root / "docs" / "brief.md"
        brief.parent.mkdir(parents=True, exist_ok=True)
        brief.write_text("# brief", encoding="utf-8")

        assignment = create_assignment(
            self.root,
            role_id="planner",
            title="Use local brief",
            proofline_link={},
            context_refs=[{"kind": "file", "path": "docs/brief.md", "label": "Brief"}],
        )

        self.assertEqual(
            assignment["context_refs"],
            [{"kind": "file", "path": "docs/brief.md", "label": "Brief"}],
        )

    def test_reject_empty_general_contract(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            create_assignment(
                self.root,
                role_id="planner",
                title="No link",
                proofline_link={},
            )

    def test_reject_empty_expected_outputs(self) -> None:
        with self.assertRaises(AssignmentValidationError):
            create_assignment(
                self.root,
                role_id="planner",
                title="Bad outputs",
                proofline_link={},
                expected_outputs=[""],
            )


if __name__ == "__main__":
    unittest.main()
