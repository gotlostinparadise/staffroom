from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from staffroom.storage.roles import create_role


class TestRoleCreation(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_create_role_writes_json_file(self) -> None:
        payload = create_role(
            self.root,
            role_id="planner",
            name="Planner",
            description="Coordinates staff",
            capabilities=["scheduling", "review"],
        )

        role_path = self.root / "staff" / "planner.json"
        self.assertTrue(role_path.exists())
        with role_path.open(encoding="utf-8") as handle:
            data = json.load(handle)

        self.assertEqual(data["role_id"], payload["role_id"])
        self.assertEqual(data["role_id"], "planner")
        self.assertEqual(data["name"], "Planner")
        self.assertEqual(data["description"], "Coordinates staff")
        self.assertEqual(data["capabilities"], ["scheduling", "review"])


if __name__ == "__main__":
    unittest.main()

