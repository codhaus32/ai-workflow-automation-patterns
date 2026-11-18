# Optional local LLM classification with Ollama

The default `rules` provider is intentionally deterministic and does not claim to be AI. The `ollama` provider sends a classification prompt and a synthetic ticket to a local Ollama service via `/api/generate`.

1. Start Ollama locally.
2. Download an available compatible model, such as `ollama pull llama3.2`.
3. Run `python -m ai_workflow_patterns run --input examples/tickets.json --provider ollama --model llama3.2 --db .state/ollama.sqlite3 --audit .state/ollama.jsonl`.

The response must be parseable JSON with `category` in `{billing, technical, sales, general}` and `priority` in `{low, normal, high}`. Invalid replies stop processing. Classification accuracy is not evaluated in this starter project, and high-priority flags are not guarantees of real-world urgency detection.

The request uses a fixed temperature for more stable outputs, and the provider retries only transient HTTP or connection failures. A local LLM may still be slow, hallucinate, or misclassify content. Add benchmark datasets and human review before deployment.
