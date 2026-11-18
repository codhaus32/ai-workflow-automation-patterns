# Security & privacy considerations

## Threat model

Ticket text is attacker-controlled. An attacker can embed instructions asking the model to ignore the classifier policy or return a command. The application only accepts two allowlisted classification fields and never executes arbitrary model output. This reduces risk but does **not** make the classifier accurate or injection-proof.

## Demonstrated controls

- Required input fields, length limits, and enum validation.
- Localhost-only Ollama endpoint in the example.
- No outbound business actions or live credentials.
- Bounded HTTP retries and timeouts.
- Metadata-only audit entries (the ticket ID itself may still be sensitive).
- Conflicting reuse of idempotency keys rejected.

## Not covered in this demo

- Authentication for human approvers, authorization, MFA, or reviewer verification.
- At-rest encryption, key management, audit log integrity protection, log rotation, data retention.
- Full prompt injection defense, model quality checks, data-loss prevention.
- Network isolation, egress policies, secret stores, sandboxed tool execution.
- Distributed worker scheduling and enterprise multi-tenant isolation.

Do not use actual customer or confidential data in the reference application as-is.
