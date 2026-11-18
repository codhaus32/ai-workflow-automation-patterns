"""Deterministic policy engine: never execute actions from model output."""

from .models import Decision, Ticket, WorkflowResult
from .providers import Classifier

ROUTES = {
    "billing": "finance_queue",
    "technical": "engineering_queue",
    "sales": "sales_queue",
    "general": "support_queue",
}


def evaluate(ticket: Ticket, classifier: Classifier) -> WorkflowResult:
    decision: Decision = classifier.classify(ticket)
    # Validate also when the injected provider is not trusted.
    decision = Decision.from_dict({"category": decision.category, "priority": decision.priority})
    return WorkflowResult(
        ticket_id=ticket.ticket_id,
        category=decision.category,
        priority=decision.priority,
        route=ROUTES[decision.category],
        status="pending_approval" if decision.priority == "high" else "routed",
    )
