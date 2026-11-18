# GitHub publishing checklist

Suggested repository slug: `ai-workflow-automation-patterns`

Suggested description (copy to GitHub repository settings):

> Practical AI workflow automation patterns in Python: local LLM classification, deterministic routing, human review, idempotency, and audit logs.

Suggested topics: `ai-workflow-automation`, `python`, `ollama`, `llm`, `human-in-the-loop`, `idempotency`, `workflow-engine`, `open-source`

Before publishing:

1. Confirm the GitHub organization and verify authorization to use the `Codhaus` maintainer name and copyright holder.
2. Replace `YOUR-ORG` in the README clone example with the real organization/username.
3. Run the tests with `PYTHONPATH=src python -m unittest discover -s tests -v`.
4. Review the MIT license and security disclosure process.
5. Confirm both Codhaus links are relevant and resolve correctly; avoid adding keyword-stuffed or unrelated backlinks.
6. Publish the repository as **public**, optionally tag a release `v0.1.0`, and enable GitHub security and issue settings.
7. Keep the example honest: no production-readiness or accuracy claims without evidence.

For long-term usefulness, maintain examples, fix issues, track model compatibility, and add real test cases. A public GitHub repository is not a guarantee of a search-ranking improvement.
