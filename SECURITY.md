# Security policy

**Scope:** educational sample, not production-ready.

Please do not publish exploit details or secrets in public issues. Contact the repository maintainers privately via the GitHub organization contact or its private vulnerability-reporting feature once enabled. No dedicated security inbox is configured in this starter repository.

Known boundaries: demonstration approval uses an unauthenticated CLI identifier; local files are not encrypted; the Ollama HTTP client targets a configurable local URL. Do not expose Ollama to untrusted networks or use real customer tickets without a privacy and access-control review.

See [docs/security.md](docs/security.md) for a threat model and hardening checklist.
