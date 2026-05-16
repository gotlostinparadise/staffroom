from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.assignments import AssignmentNotFoundError, get_assignment_status


class TestAssignmentMissing(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_missing_assignment_status(self) -> None:
        with self.assertRaises(AssignmentNotFoundError):
            get_assignment_status(self.root, "asg_12345678")


if __name__ == "__main__":
    unittest.main()

