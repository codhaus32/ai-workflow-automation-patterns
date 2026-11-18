"""Metadata-only append-only audit events for the educational demo."""

import json
from datetime import datetime, timezone
from pathlib import Path


def record_event(path: str | Path, *, event: str, ticket_id: str, status: str, category: str, priority: str):
    """Do not include ticket bodies, prompts, model completions, or approver IDs."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "ticket_id": ticket_id,
        "status": status,
        "category": category,
        "priority": priority,
    }
    with output.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")
