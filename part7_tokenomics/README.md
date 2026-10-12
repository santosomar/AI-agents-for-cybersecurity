# Part 7: Tokenomics for Security Agents

Parts 1–6 show how to build and choose agents. Part 7 is about what they cost to run, and how to measure that cost in a way that leads to better decisions.

The short version:

1. **Agents are expensive because they loop.** Every call to a stateless model API re-sends the system prompt, tool schemas, history, and every tool result so far. Input tokens grow with each turn, so total spend grows roughly with the *square* of the task length.
2. **Six levers control most of the bill:** prompt caching, model routing, compaction, fewer tools, batch processing, and budgets.
3. **Price per token is the wrong metric.** The metric that matters is **cost per accepted outcome**, and in security work the largest term is usually people reviewing the agent's output.

```
                          model + runtime + human review
  cost per accepted fix = ------------------------------
                                 acceptance rate
```

> A SOC agent that costs $0.02 per task really costs about $3.02 per answer when 40% of its answers need 15 minutes of review at $30 an hour. ([Splunk, 2026](https://www.splunk.com/en_us/blog/artificial-intelligence/what-is-agent-tokenomics.html))

## Where the money goes

![Cumulative input tokens over a 20-turn task](docs/images/context_growth.png)

With a 4k-token base and 2k tokens added per turn, a 20-turn task sends **460k** input tokens with no context management. Compacting whenever the context passes 20k tokens cuts that to **250k** (46% fewer). By the fourth call of a typical tool loop, **76%** of the input is context the model has already processed. Both numbers are reproduced by `01_context_growth.py`.

## The six levers

| # | Lever | One-line rule | Write-up | Example |
|---|-------|---------------|----------|---------|
| 1 | Prompt caching | Reuse the stable prefix at 5–10% of the input price | [03](docs/03_prompt_caching.md) | `02_prompt_caching.py`, `03_live_cache_check.py` |
| 2 | Model routing | Small model first; escalate only when needed | [04](docs/04_model_routing.md) | `05_model_routing.py` |
| 3 | Compaction | Summarize old turns; trim large tool output | [02](docs/02_context_compounding_and_compaction.md) | `01_context_growth.py`, `06_tool_schema_overhead.py` |
| 4 | Fewer tools | Every tool schema is paid for on every request | [05](docs/05_fewer_tools_batch_and_budgets.md) | `06_tool_schema_overhead.py` |
| 5 | Batch | Run offline work at roughly half price | [05](docs/05_fewer_tools_batch_and_budgets.md) | `08_batch_triage.py` |
| 6 | Budgets | Set a token and cost ceiling per task | [05](docs/05_fewer_tools_batch_and_budgets.md) | `07_token_budget_guard.py` |

The levers stack. A batch job with a cached prefix on a routed small model can cost well under a tenth of the naive version (see the output of `08_batch_triage.py`).

## Write-ups

Read these in order. Each one explains the mechanism, shows the math, and ends with security-specific advice.

1. [How tokens are billed](docs/01_how_tokens_are_billed.md): input, output, reasoning, cached tokens, service tiers, long-context pricing, and an October 2026 price snapshot
2. [Context compounding and compaction](docs/02_context_compounding_and_compaction.md): why agent cost grows quadratically, and how to bend the curve
3. [Prompt caching](docs/03_prompt_caching.md): provider mechanics, TTLs, break-even math, prompt layout, and cache security
4. [Model routing](docs/04_model_routing.md): routers, cascades, the escalation trap, and how to decide which steps to move
5. [Fewer tools, batch, and budgets](docs/05_fewer_tools_batch_and_budgets.md): tool-schema overhead, tool-output caps, Batch APIs, and denial-of-wallet defenses
6. [Cost per outcome](docs/06_cost_per_outcome.md): the metric that matters, the hidden human term, and why an expensive model can be cheaper
7. [Choosing models with the Cyber Index](docs/07_cyber_index.md): reading a cost-aware benchmark for defensive agents

## Examples

All examples share one price sheet, [`pricing.yaml`](pricing.yaml), and one helper module, [`token_math.py`](token_math.py). Prices change often: update the YAML file, not the scripts.

| Script | What it shows | Needs |
|--------|---------------|-------|
| `01_context_growth.py` | Re-sent context per call; 20-turn growth with and without compaction; cost on five models. `--plot` saves the chart | Offline |
| `02_prompt_caching.py` | One day of SOC triage with and without caching; 5-minute vs 1-hour TTL; break-even; the "timestamp first" mistake | Offline |
| `03_live_cache_check.py` | Real `cached_tokens` and `cache_write_tokens` from the OpenAI Responses API across repeated calls | `OPENAI_API_KEY` |
| `04_cost_per_outcome.py` | The Splunk $3.02 example; cheap vs frontier model per accepted fix; sensitivity grid; backlog cost from benchmark pass rates | Offline |
| `05_model_routing.py` | Intent router for a day of SOC work; cascade economics and the escalation trap; Pydantic-validated cascade | Offline |
| `06_tool_schema_overhead.py` | Real token counts for 14 security tool schemas; pruning by intent; capping and summarizing nmap output | Offline (tiktoken downloads its encoding once) |
| `07_token_budget_guard.py` | Per-task token, dollar, and loop ceilings on healthy, stuck, and prompt-injected agents. `--live` enforces it in a LangChain agent | Offline, or `OPENAI_API_KEY` with `--live` |
| `08_batch_triage.py` | Builds an OpenAI Batch JSONL for 5,000 scanner findings and prices standard vs batch vs batch + cache. `--submit` sends it | Offline, or `OPENAI_API_KEY` with `--submit` |

Run them from the repository root:

```bash
uv sync --python python3.13
uv run python part7_tokenomics/01_context_growth.py --plot
uv run python part7_tokenomics/02_prompt_caching.py --alerts 500 --gap 2
uv run python part7_tokenomics/04_cost_per_outcome.py
uv run python part7_tokenomics/07_token_budget_guard.py --live
```

Generated files (charts, batch JSONL) go to `part7_tokenomics/output/`, which is gitignored.

## Directory layout

```
part7_tokenomics/
├── README.md                     ← this file
├── pricing.yaml                  ← price sheet used by every example (Oct 2026 snapshot)
├── token_math.py                 ← shared cost helpers
├── 01_context_growth.py          ← context compounding and compaction
├── 02_prompt_caching.py          ← caching calculator
├── 03_live_cache_check.py        ← real cache hits on the OpenAI API
├── 04_cost_per_outcome.py        ← cost per accepted fix
├── 05_model_routing.py           ← routers and cascades
├── 06_tool_schema_overhead.py    ← tool schemas and tool output
├── 07_token_budget_guard.py      ← per-task ceilings and loop detection
├── 08_batch_triage.py            ← Batch API job builder
└── docs/                         ← detailed write-ups (01–07) and images
```

## Security takeaways

Tokenomics is also a security topic:

- **Unbounded consumption is a vulnerability.** [OWASP LLM10:2025](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/) covers it. A prompt-injected page that makes your agent loop is a denial-of-wallet attack. Budgets and loop detection are controls, not just cost hygiene.
- **Shared caches can leak.** Keep secrets and per-tenant data out of shared prefixes, and partition caches per tenant.
- **Fewer tools means a smaller blast radius.** A step that cannot see `edr_isolate_host` cannot be tricked into calling it.
- **Trimming tool output must not destroy evidence.** Keep raw tool output in storage, and give the model a summary plus a pointer to it.
- **Batch files are data at rest.** Redact them, and delete them when the job is done.
- **Part 8 adopts these ceilings.** The [multi-agent harness spec](../part8_multi-agent_harness_spec/safety-governance.md) pauses new work at 80% of a budget and hard-stops at 100%, using the same pattern as `07_token_budget_guard.py`.

> **Note:** Prices and model names were researched in October 2026 from the provider pages listed in [`pricing.yaml`](pricing.yaml). Discounts vary by provider, model, and region. Check the current price sheets before making decisions.
