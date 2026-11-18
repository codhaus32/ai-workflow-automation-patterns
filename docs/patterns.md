# Reliable AI workflow patterns

| Pattern | What it prevents | Demonstration |
|---|---|---|
| Structured output validation | Untrusted arbitrary model text becoming a command | `Decision.from_dict` |
| Deterministic policy | Model secretly choosing a side effect | `engine.ROUTES` |
| Idempotency key + content fingerprint | Accidental repeated processing and reused identifiers | `WorkflowStore.run_once` |
| Human review gate | High-priority tickets proceeding without review | `pending_approval` and `approve` CLI |
| Bounded exponential backoff | Unbounded retries and service overload | `OllamaClassifier.classify` |
| Metadata-only audit | Sensitive ticket content in ordinary log lines | `audit.record_event` |

## Workflow examples beyond support tickets

- **Invoice exception review:** extract an invoice discrepancy, flag large mismatches, require finance approval. Do not let model output authorize a transfer.
- **Lead qualification:** summarize inbound inquiries and suggest a team, then use CRM APIs only after validating recipients and permissions.
- **Document ingestion:** parse contracts, detect missing fields, send ambiguous clauses to legal review before any final decision.
- **Internal IT triage:** prioritize incidents and recommend a runbook, but require explicit approval for destructive operations.

## Design rules

Treat LLM results as *untrusted suggestions*, not authority. Use narrow schemas, explicit policy boundaries, small permissions, and real observability. Consider eventual consistency when adding queues and external integrations. Avoid telling users the system is autonomous when the implementation requires human intervention.
