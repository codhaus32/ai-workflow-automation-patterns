"""Demo command-line interface. No outbound workflow actions are performed."""

import argparse
import json
import sys
from pathlib import Path

from .audit import record_event
from .engine import evaluate
from .models import Ticket
from .providers import OllamaClassifier, RulesClassifier
from .storage import WorkflowStore


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Safe AI workflow reference demo")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Classify and simulate routing")
    run.add_argument("--input", required=True, help="Path to JSON list of example tickets")
    run.add_argument("--provider", choices=("rules", "ollama"), default="rules")
    run.add_argument("--model", default="llama3.2", help="Local Ollama model name")
    approve = commands.add_parser("approve", help="Approve pending ticket (metadata only)")
    approve.add_argument("--ticket-id", required=True)
    approve.add_argument("--approver", required=True, help="Demo identifier; no authentication")
    for command in (run, approve):
        command.add_argument("--db", default=".state/workflows.sqlite3")
        command.add_argument("--audit", default=".state/audit.jsonl")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    store = None
    try:
        store = WorkflowStore(args.db)
        results = []
        if args.command == "run":
            source = json.loads(Path(args.input).read_text(encoding="utf-8"))
            if not isinstance(source, list) or len(source) > 1000:
                raise ValueError("Input must be a JSON array containing at most 1,000 tickets")
            classifier = RulesClassifier() if args.provider == "rules" else OllamaClassifier(model=args.model)
            for item in source:
                ticket = Ticket.from_dict(item)
                result, created = store.run_once(ticket, lambda t: evaluate(t, classifier))
                if created:
                    record_event(args.audit, event="evaluated", ticket_id=ticket.ticket_id, status=result.status,
                                 category=result.category, priority=result.priority)
                results.append({**result.to_dict(), "created": created})
        else:
            result, updated = store.approve(args.ticket_id, args.approver)
            if updated:
                record_event(args.audit, event="approved", ticket_id=result.ticket_id, status=result.status,
                             category=result.category, priority=result.priority)
            results.append({**result.to_dict(), "updated": updated})
        print(json.dumps(results, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if store is not None:
            store.close()


if __name__ == "__main__":
    raise SystemExit(main())
