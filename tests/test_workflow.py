import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from ai_workflow_patterns.audit import record_event
from ai_workflow_patterns.engine import evaluate
from ai_workflow_patterns.models import Decision, Ticket
from ai_workflow_patterns.providers import RulesClassifier, OllamaClassifier
from ai_workflow_patterns.storage import IdempotencyConflict, WorkflowStore


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = WorkflowStore(Path(self.temp.name) / "workflow.sqlite3")
        self.classifier = RulesClassifier()

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_classification_and_routing(self):
        ticket = Ticket("A1", "Invoice incorrect", "I was charged twice")
        result = evaluate(ticket, self.classifier)
        self.assertEqual(result.category, "billing")
        self.assertEqual(result.route, "finance_queue")
        self.assertEqual(result.status, "routed")

    def test_high_priority_requires_review_and_approval(self):
        ticket = Ticket("A2", "URGENT API outage", "Critical downtime")
        result, created = self.store.run_once(ticket, lambda t: evaluate(t, self.classifier))
        self.assertTrue(created)
        self.assertEqual(result.status, "pending_approval")
        approved, updated = self.store.approve("A2", "reviewer-1")
        self.assertTrue(updated)
        self.assertEqual(approved.status, "approved")
        again, updated = self.store.approve("A2", "reviewer-1")
        self.assertFalse(updated)
        self.assertEqual(again.status, "approved")

    def test_idempotency_and_conflict(self):
        ticket = Ticket("A3", "Sales demo", "Interested in a demo")
        first, created = self.store.run_once(ticket, lambda t: evaluate(t, self.classifier))
        self.assertTrue(created)
        second, created = self.store.run_once(ticket, lambda t: 1 / 0)
        self.assertFalse(created)
        self.assertEqual(first, second)
        with self.assertRaises(IdempotencyConflict):
            self.store.run_once(Ticket("A3", "Changed", "New text"), lambda t: evaluate(t, self.classifier))

    def test_invalid_input_and_model_output(self):
        with self.assertRaises(ValueError):
            Ticket.from_dict({"id": "X", "subject": "", "body": "Hi"})
        with self.assertRaises(ValueError):
            Decision.from_dict({"category": "execute_shell", "priority": "high"})
        with self.assertRaises(ValueError):
            OllamaClassifier(base_url="https://example.org")

    def test_keyword_boundaries(self):
        ticket = Ticket("A6", "Download complete", "I downloaded the report")
        decision = RulesClassifier().classify(ticket)
        self.assertEqual(decision.priority, "normal")

    def test_ollama_json_response_validation(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, maximum):
                return json.dumps({"response": json.dumps({"category": "technical", "priority": "high"})}).encode()
        with patch("ai_workflow_patterns.providers.request.urlopen", return_value=FakeResponse()):
            decision = OllamaClassifier().classify(Ticket("A7", "Bug", "An error occurred"))
        self.assertEqual(decision, Decision("technical", "high"))
        with self.assertRaises(ValueError):
            OllamaClassifier(base_url="http://localhost:1234@evil.example")

    def test_audit_omits_ticket_body(self):
        path = Path(self.temp.name) / "audit.jsonl"
        record_event(path, event="evaluated", ticket_id="A4", status="routed", category="general", priority="normal")
        line = path.read_text(encoding="utf-8")
        event = json.loads(line)
        self.assertEqual(event["ticket_id"], "A4")
        self.assertNotIn("body", event)
        self.assertNotIn("prompt", event)
        self.assertNotIn("approver", event)

    def test_approval_not_allowed_for_normal_ticket(self):
        ticket = Ticket("A5", "Hi", "Hello team")
        self.store.run_once(ticket, lambda t: evaluate(t, self.classifier))
        with self.assertRaises(ValueError):
            self.store.approve("A5", "reviewer")


if __name__ == "__main__":
    unittest.main()
