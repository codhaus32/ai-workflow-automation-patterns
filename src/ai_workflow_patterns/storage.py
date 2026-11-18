"""SQLite-backed demo persistence with idempotency and a human approval gate."""

import hashlib
import json
import sqlite3
from pathlib import Path

from .models import Ticket, WorkflowResult


class IdempotencyConflict(ValueError):
    """Same ticket ID was submitted with a different payload."""


class WorkflowStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path), timeout=10)
        self.connection.execute("PRAGMA busy_timeout=10000")
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                ticket_id TEXT PRIMARY KEY,
                payload_hash TEXT NOT NULL,
                result_json TEXT NOT NULL,
                approver TEXT
            )
        """)
        self.connection.commit()

    def close(self):
        self.connection.close()

    @staticmethod
    def fingerprint(ticket: Ticket) -> str:
        canonical = json.dumps(ticket.payload(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def run_once(self, ticket: Ticket, evaluator) -> tuple[WorkflowResult, bool]:
        """Returns (result, created). Serializes SQLite writes using BEGIN IMMEDIATE.

        Model classification occurs in the transaction in this small demo to
        guarantee single processing; production implementations should use a
        lease + state machine rather than holding a lock during model calls.
        """
        fingerprint = self.fingerprint(ticket)
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT payload_hash, result_json FROM workflows WHERE ticket_id=?", (ticket.ticket_id,)
            ).fetchone()
            if row:
                if row[0] != fingerprint:
                    raise IdempotencyConflict(f"Ticket ID {ticket.ticket_id!r} was already used for different content")
                self.connection.commit()
                return WorkflowResult(**json.loads(row[1])), False
            result = evaluator(ticket)
            self.connection.execute(
                "INSERT INTO workflows (ticket_id, payload_hash, result_json) VALUES (?, ?, ?)",
                (ticket.ticket_id, fingerprint, json.dumps(result.to_dict())),
            )
            self.connection.commit()
            return result, True
        except Exception:
            self.connection.rollback()
            raise

    def approve(self, ticket_id: str, approver: str) -> tuple[WorkflowResult, bool]:
        """Marks pending item approved. Does not perform an outbound action.

        Approver string is demo metadata only, not verified authentication.
        """
        if not approver.strip() or len(approver) > 100:
            raise ValueError("Approver must be a nonempty identifier of <= 100 characters")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT result_json FROM workflows WHERE ticket_id=?", (ticket_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"Unknown ticket ID {ticket_id!r}")
            stored = WorkflowResult(**json.loads(row[0]))
            if stored.status == "approved":
                self.connection.commit()
                return stored, False
            if stored.status != "pending_approval":
                raise ValueError(f"Ticket {ticket_id!r} does not require approval")
            updated = WorkflowResult(
                ticket_id=stored.ticket_id,
                category=stored.category,
                priority=stored.priority,
                route=stored.route,
                status="approved",
            )
            self.connection.execute(
                "UPDATE workflows SET result_json=?, approver=? WHERE ticket_id=?",
                (json.dumps(updated.to_dict()), approver, ticket_id),
            )
            self.connection.commit()
            return updated, True
        except Exception:
            self.connection.rollback()
            raise
