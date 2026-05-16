from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.work_types import (
    WorkTypeError,
    WorkTypeValidationError,
    create_work_type,
    get_work_type,
    list_work_types,
)


class TestWorkTypes(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_create_show_and_list_work_type(self) -> None:
        work_type = create_work_type(
            self.root,
            work_type_id="research",
            name="Research",
            description="Collect and cite facts",
            default_expected_outputs=["summary", "sources"],
            allowed_evidence_kinds=["url", "file"],
            recommended_role_ids=["researcher"],
        )

        self.assertEqual(work_type["work_type_id"], "research")
        self.assertEqual(work_type["name"], "Research")
        self.assertEqual(work_type["default_expected_outputs"], ["summary", "sources"])
        self.assertEqual(work_type["allowed_evidence_kinds"], ["url", "file"])
        self.assertEqual(work_type["recommended_role_ids"], ["researcher"])
        self.assertEqual(get_work_type(self.root, "research"), work_type)
        self.assertEqual([item["work_type_id"] for item in list_work_types(self.root)], ["research"])

    def test_reject_duplicate_and_invalid_work_type(self) -> None:
        create_work_type(self.root, "review", "Review")
        with self.assertRaises(WorkTypeError):
            create_work_type(self.root, "review", "Duplicate")

        with self.assertRaises(WorkTypeValidationError):
            create_work_type(self.root, "Review Work", "Review")

    def test_reject_empty_expected_outputs(self) -> None:
        with self.assertRaises(WorkTypeValidationError):
            create_work_type(self.root, "analysis", "Analysis", default_expected_outputs=[""])


if __name__ == "__main__":
    unittest.main()
