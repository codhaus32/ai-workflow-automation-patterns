"""Input, decision and result models with validation at trust boundaries."""

from dataclasses import asdict, dataclass
from typing import Literal

CATEGORIES = frozenset({"billing", "technical", "sales", "general"})
PRIORITIES = frozenset({"low", "normal", "high"})


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    subject: str
    body: str

    @classmethod
    def from_dict(cls, raw: dict) -> "Ticket":
        if not isinstance(raw, dict):
            raise ValueError("Each ticket must be a JSON object")
        ticket_id, subject, body = raw.get("id"), raw.get("subject"), raw.get("body")
        for label, value, maximum in (("id", ticket_id, 128), ("subject", subject, 500), ("body", body, 5000)):
            if not isinstance(value, str) or not value.strip() or len(value) > maximum:
                raise ValueError(f"ticket {label} must be a nonempty string of <= {maximum} characters")
        return cls(ticket_id, subject, body)

    def payload(self) -> dict:
        return {"id": self.ticket_id, "subject": self.subject, "body": self.body}


@dataclass(frozen=True)
class Decision:
    category: str
    priority: str

    @classmethod
    def from_dict(cls, value: dict) -> "Decision":
        if not isinstance(value, dict):
            raise ValueError("Classifier output must be a JSON object")
        category, priority = value.get("category"), value.get("priority")
        if category not in CATEGORIES:
            raise ValueError(f"Unsupported category: {category!r}")
        if priority not in PRIORITIES:
            raise ValueError(f"Unsupported priority: {priority!r}")
        return cls(category=category, priority=priority)


@dataclass(frozen=True)
class WorkflowResult:
    ticket_id: str
    category: str
    priority: str
    route: str
    status: Literal["routed", "pending_approval", "approved"]

    def to_dict(self) -> dict:
        return asdict(self)
