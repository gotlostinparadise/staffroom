from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.roles import RoleError, RoleValidationError, create_role


class TestRoleValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_reject_invalid_role_id(self) -> None:
        with self.assertRaises(RoleValidationError):
            create_role(self.root, role_id="Invalid_ID", name="Bad")

    def test_reject_empty_name(self) -> None:
        with self.assertRaises(RoleValidationError):
            create_role(self.root, role_id="badname", name="")

    def test_reject_duplicate_role(self) -> None:
        create_role(self.root, role_id="planner", name="Planner")
        with self.assertRaises(RoleError):
            create_role(self.root, role_id="planner", name="Planner duplicate")


if __name__ == "__main__":
    unittest.main()

