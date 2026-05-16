from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from staffroom.storage.assignments import (
    AssignmentStateError,
    AssignmentValidationError,
    add_assignment_evidence,
    add_assignment_note,
    assign_assignment,
    close_assignment,
    create_assignment,
    list_assignments,
    start_assignment,
    submit_assignment,
)
from staffroom.storage.roles import create_role
from staffroom.storage.workers import create_worker


class TestSupervisorProtocol(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        create_role(self.root, role_id="planner", name="Planner")
        create_role(self.root, role_id="reviewer", name="Reviewer")
        create_worker(self.root, "agent-reviewer-1", "Agent Reviewer", "agent", ["review"])
        self.run_manifest = self.root / "runs" / "staffroom-mvp" / "MANIFEST.json"
        self.run_manifest.parent.mkdir(parents=True, exist_ok=True)
        self.run_manifest.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def create_assignment_for(self, role_id: str = "planner", title: str = "Protocol check") -> dict:
        return create_assignment(
            self.root,
            role_id=role_id,
            title=title,
            proofline_link={"proofline_run": "runs/staffroom-mvp/MANIFEST.json"},
        )

    def test_supervisor_assigns_pending_work_to_agent(self) -> None:
        assignment = self.create_assignment_for()
        assigned = assign_assignment(
            self.root,
            assignment["assignment_id"],
            agent_id="agent-reviewer-1",
            supervisor_id="lead",
        )

        self.assertEqual(assigned["status"], "assigned")
        self.assertEqual(assigned["assigned_agent_id"], "agent-reviewer-1")
        self.assertEqual(assigned["assigned_worker_id"], "agent-reviewer-1")
        self.assertEqual(assigned["assigned_by"], "lead")
        self.assertIn("assigned_at_utc", assigned)
        self.assertIn("updated_at_utc", assigned)
        self.assertEqual(assigned["events"][-1]["type"], "assigned")

    def test_assigned_agent_starts_and_submits_for_review(self) -> None:
        assignment = self.create_assignment_for()
        assign_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-1")

        active = start_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-1")
        self.assertEqual(active["status"], "active")
        self.assertIn("started_at_utc", active)
        self.assertEqual(active["events"][-1]["type"], "started")

        reviewed = submit_assignment(
            self.root,
            assignment["assignment_id"],
            agent_id="agent-reviewer-1",
            notes="Ready for supervisor review",
        )
        self.assertEqual(reviewed["status"], "review")
        self.assertEqual(reviewed["submitted_by_agent_id"], "agent-reviewer-1")
        self.assertEqual(reviewed["events"][-1]["type"], "submitted")

        closed = close_assignment(
            self.root,
            assignment["assignment_id"],
            result="done",
            notes="accepted",
            closed_by="lead",
        )
        self.assertEqual(closed["status"], "closed")
        self.assertEqual(closed["closed_by"], "lead")

    def test_wrong_agent_cannot_start_or_submit(self) -> None:
        assignment = self.create_assignment_for()
        assign_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-1")

        with self.assertRaises(AssignmentStateError):
            start_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-2")

        start_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-1")
        with self.assertRaises(AssignmentStateError):
            submit_assignment(
                self.root,
                assignment["assignment_id"],
                agent_id="agent-reviewer-2",
                notes="wrong agent",
            )

    def test_note_and_evidence_are_appended(self) -> None:
        assignment = self.create_assignment_for()
        assign_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-1")
        start_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-1")

        noted = add_assignment_note(
            self.root,
            assignment["assignment_id"],
            agent_id="agent-reviewer-1",
            text="Investigating",
        )
        self.assertEqual(noted["events"][-1]["type"], "note")
        self.assertEqual(noted["events"][-1]["message"], "Investigating")

        evidence_file = self.root / "runs" / "staffroom-mvp" / "artifacts" / "evidence.txt"
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        evidence_file.write_text("ok", encoding="utf-8")
        with_evidence = add_assignment_evidence(
            self.root,
            assignment["assignment_id"],
            agent_id="agent-reviewer-1",
            kind="test-output",
            path="runs/staffroom-mvp/artifacts/evidence.txt",
            summary="unit test output",
        )
        self.assertEqual(with_evidence["evidence"][-1]["kind"], "test-output")
        self.assertEqual(with_evidence["evidence"][-1]["path"], "runs/staffroom-mvp/artifacts/evidence.txt")
        self.assertEqual(with_evidence["events"][-1]["type"], "evidence_added")

    def test_evidence_rejects_invalid_paths(self) -> None:
        assignment = self.create_assignment_for()
        assign_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-1")
        start_assignment(self.root, assignment["assignment_id"], agent_id="agent-reviewer-1")

        with self.assertRaises(AssignmentValidationError):
            add_assignment_evidence(
                self.root,
                assignment["assignment_id"],
                agent_id="agent-reviewer-1",
                kind="test-output",
                path="missing.txt",
            )

        with self.assertRaises(AssignmentValidationError):
            add_assignment_evidence(
                self.root,
                assignment["assignment_id"],
                agent_id="agent-reviewer-1",
                kind="test-output",
                path="/tmp/outside.txt",
            )

    def test_list_assignments_filters_by_state_role_and_agent(self) -> None:
        planner_assignment = self.create_assignment_for("planner", "Plan")
        reviewer_assignment = self.create_assignment_for("reviewer", "Review")
        create_worker(self.root, "agent-planner", "Agent Planner", "agent", ["planning"])
        create_worker(self.root, "agent-reviewer", "Agent Reviewer", "agent", ["review"])
        assign_assignment(self.root, planner_assignment["assignment_id"], agent_id="agent-planner")
        assign_assignment(self.root, reviewer_assignment["assignment_id"], agent_id="agent-reviewer")

        assigned = list_assignments(self.root, state="assigned")
        self.assertEqual({item["assignment_id"] for item in assigned}, {
            planner_assignment["assignment_id"],
            reviewer_assignment["assignment_id"],
        })

        planner_items = list_assignments(self.root, role_id="planner")
        self.assertEqual([item["assignment_id"] for item in planner_items], [planner_assignment["assignment_id"]])

        reviewer_items = list_assignments(self.root, agent_id="agent-reviewer")
        self.assertEqual([item["assignment_id"] for item in reviewer_items], [reviewer_assignment["assignment_id"]])

        worker_items = list_assignments(self.root, worker_id="agent-reviewer")
        self.assertEqual([item["assignment_id"] for item in worker_items], [reviewer_assignment["assignment_id"]])

    def test_assignment_can_be_assigned_to_worker(self) -> None:
        assignment = self.create_assignment_for()

        assigned = assign_assignment(
            self.root,
            assignment["assignment_id"],
            worker_id="agent-reviewer-1",
            supervisor_id="lead",
        )

        self.assertEqual(assigned["assigned_worker_id"], "agent-reviewer-1")
        self.assertEqual(assigned["assigned_agent_id"], "agent-reviewer-1")

    def test_reject_assignment_to_unknown_worker(self) -> None:
        assignment = self.create_assignment_for()

        with self.assertRaises(AssignmentValidationError):
            assign_assignment(self.root, assignment["assignment_id"], worker_id="missing-worker")

        with self.assertRaises(AssignmentValidationError):
            assign_assignment(self.root, assignment["assignment_id"], worker_id="../bad")


if __name__ == "__main__":
    unittest.main()
