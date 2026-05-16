from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.workers import (
    WorkerError,
    WorkerValidationError,
    create_worker,
    get_worker,
    list_workers,
)


class TestWorkers(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_create_show_and_list_worker_profile(self) -> None:
        worker = create_worker(
            self.root,
            worker_id="agent-reviewer-1",
            display_name="Agent Reviewer",
            worker_kind="agent",
            capabilities=["review", "tests"],
        )

        self.assertEqual(worker["worker_id"], "agent-reviewer-1")
        self.assertEqual(worker["display_name"], "Agent Reviewer")
        self.assertEqual(worker["worker_kind"], "agent")
        self.assertEqual(worker["capabilities"], ["review", "tests"])
        self.assertIn("created_at_utc", worker)
        self.assertEqual(get_worker(self.root, "agent-reviewer-1"), worker)
        self.assertEqual([item["worker_id"] for item in list_workers(self.root)], ["agent-reviewer-1"])

    def test_list_workers_filters_by_kind_and_capability(self) -> None:
        create_worker(self.root, "human-writer", "Human Writer", "human", ["writing"])
        create_worker(self.root, "agent-reviewer", "Agent Reviewer", "agent", ["review"])
        create_worker(self.root, "agent-coder", "Agent Coder", "agent", ["coding", "review"])

        self.assertEqual(
            [item["worker_id"] for item in list_workers(self.root, worker_kind="agent")],
            ["agent-coder", "agent-reviewer"],
        )
        self.assertEqual(
            [item["worker_id"] for item in list_workers(self.root, capability="review")],
            ["agent-coder", "agent-reviewer"],
        )

    def test_reject_duplicate_worker_id(self) -> None:
        create_worker(self.root, "agent-reviewer", "Agent Reviewer", "agent", [])
        with self.assertRaises(WorkerError):
            create_worker(self.root, "agent-reviewer", "Duplicate", "agent", [])

    def test_reject_invalid_worker_id_and_kind(self) -> None:
        with self.assertRaises(WorkerValidationError):
            create_worker(self.root, "Agent Reviewer", "Agent Reviewer", "agent", [])

        with self.assertRaises(WorkerValidationError):
            create_worker(self.root, "agent-reviewer", "Agent Reviewer", "robot", [])


if __name__ == "__main__":
    unittest.main()
