# 5. Fewer Tools, Batch, and Budgets

Three levers that are easy to apply and easy to forget.

---

## Fewer tools: every schema is paid for on every request

When you give an agent tools, the framework sends each tool's name, description, and JSON parameter schema to the model **on every call**. The model needs them to decide what to call. Those tokens sit at the front of the prompt, before the alert, and you pay for them every turn.

`06_tool_schema_overhead.py` counts a typical security toolset with tiktoken:

| Toolset | Tools | Tokens per request |
|---------|-----:|------------------:|
| Everything (nmap, KEV, Shodan, Splunk, VirusTotal, WHOIS, DNS, NVD, EDR, Jira, GitHub, Slack) | 14 | 881 |
| `enrich_ioc` intent only | 5 | 259 (71% fewer) |
| `vuln_triage` intent only | 3 | 182 (79% fewer) |
| `hunt` intent only | 1 | 79 (91% fewer) |

These schemas are deliberately terse. Real MCP servers often expose 20–50 tools with paragraph-long descriptions, and connecting three or four servers can put **10,000–25,000 tokens** of schemas in front of every call. One community MCP router measured a 26k-token catalog shrinking to about 900 tokens by exposing only `get_tool_schema` and `invoke_tool`.

### Ways to cut tool overhead

1. **Scope tools per step or per subagent.** An enrichment subagent needs enrichment tools, not EDR containment.
2. **Select tools by intent.** Classify the task first (with rules or a small model), then attach only the matching tool group. MCP proposal SEP-1576 describes embedding-based top-k tool selection for this.
3. **Lazy-load schemas.** Expose a compact catalog of names plus a `get_tool_schema` tool, and fetch full schemas only when needed. This costs one extra round-trip on first use.
4. **Write short descriptions.** One sentence on what the tool does and when to use it. Move long usage guidance into the tool's error messages, which only appear when the model gets it wrong.
5. **Keep the order stable** so the schemas stay in the cached prefix (see [write-up 3](03_prompt_caching.md)).

### Cap tool output

Tool output is the other half of the problem. It enters the context once and is re-sent on every later turn. A 64-host nmap scan is about 6,500 tokens. Two ways to shrink it:

| Approach | Tokens | Trade-off |
|----------|------:|-----------|
| Raw output | 6,549 | Everything, re-sent every turn |
| Head + tail cap at 600 tokens | 609 | Generic, but loses the middle where findings often are |
| Domain-aware summary (open services, rarest first, with hosts) | 175 | Keeps every finding; needs a parser per tool |

Prefer structured summaries for tools you call often (nmap, Splunk, EDR), and use a generic cap as a safety net for everything else.

**Security notes:** Fewer visible tools means a smaller blast radius. A triage step that cannot see `edr_isolate_host` cannot be prompt-injected into calling it. Capping tool output also limits how much attacker-controlled text (from web pages, emails, or log lines) reaches the model. Always keep the raw output in storage so an analyst can audit it.

---

## Batch: offline work at roughly half price

OpenAI, Anthropic, and Google all offer a Batch API at **50% of the standard rate**. You upload a file of requests, and results arrive within 24 hours (usually much sooner). Cache discounts stack on top.

`08_batch_triage.py` builds a batch of 5,000 scanner findings on gpt-6.1-sol:

| Mode | Cost |
|------|-----:|
| Standard, synchronous | $29.60 |
| Batch (0.5×) | $14.80 |
| Batch + cached 2,500-token prefix | $2.93 |

Each line of an OpenAI batch file is one request:

```json
{"custom_id": "finding-00000", "method": "POST", "url": "/v1/responses",
 "body": {"model": "gpt-6.1-sol", "instructions": "You are a vulnerability management analyst...",
          "input": "Host 10.20.77.102: TLS 1.0 and TLS 1.1 enabled on port 443.", "max_output_tokens": 120}}
```

### Good batch work in a security program

- Re-scoring or re-classifying yesterday's closed alerts with a new prompt
- Enriching a backlog of vulnerability scanner findings
- Tagging CVEs or detections with MITRE ATT&CK techniques
- Generating detection-rule documentation
- **Evals:** replaying a golden set of incidents against a new model or prompt before rollout

### Bad batch work

Anything a person or an agent loop is waiting on. An agent's next step depends on the previous answer, so agent loops cannot be batched. Use Flex (also 0.5× on OpenAI and Gemini, synchronous but best-effort) for non-urgent pipelines that still need sequential calls.

**Security notes:** Batch input and output files are data at rest on your disk and in provider storage. Redact secrets and personal data before writing them, set retention, and delete files when the job is done. Treat batch outputs like any other untrusted model output: validate them against a schema before they update a ticketing or asset system.

---

## Budgets: a token and cost ceiling per task

Agents loop, and sometimes they loop forever. A stuck agent re-runs the same search because the results "look incomplete". A prompt-injected agent follows a web page that tells it to fetch ever-larger pages. Without a ceiling, the only limit is your credit card.

OWASP calls this **LLM10:2025 Unbounded Consumption**. When an attacker triggers it on purpose, it is a **denial-of-wallet** attack.

`07_token_budget_guard.py` enforces four limits per task:

| Limit | Catches |
|-------|---------|
| Max input tokens | Context blow-ups (huge tool output, injected pages) |
| Max output tokens | Runaway reasoning or generation |
| Max dollars | Everything, in the unit finance cares about |
| Max identical tool calls | Loops: the same tool with the same arguments, again and again |

Simulated results on gpt-6.1-sol with a $0.50 ceiling:

| Scenario | Outcome |
|----------|---------|
| Healthy investigation (3 tools, then answer) | Finished: 4 calls, $0.10 |
| Stuck agent repeating one Splunk search | Stopped on the third identical call |
| Prompt-injected page chain (30k tokens per fetch) | Stopped at 206k input tokens, before the dollar limit |

### Implementing budgets

- **In LangChain 1.x**, use `ModelCallLimitMiddleware(run_limit=...)` and `ToolCallLimitMiddleware(...)` for call counts. For token and dollar limits, use a callback that reads `usage_metadata` (as in `07_token_budget_guard.py --live`).
- **At the gateway.** LiteLLM, cloud AI gateways, and observability platforms such as Splunk Agent Observability can enforce per-key and per-team budgets and alert on runaway agents. Gateway limits are harder for a compromised agent to bypass than in-process limits.
- **At the provider.** Set organization and project spend limits and alerts as the last line of defense.

### When a budget trips

**Fail closed.** Stop the agent, save the partial work and the reason, and hand the task to a human. Do not silently retry with a bigger budget; that is how a one-off loop becomes a pattern. Log every trip: a cluster of budget trips on one alert source is a strong signal that someone is feeding your agent hostile input.

### Setting the number

Replay representative tasks at several budgets, keeping the model, tools, and acceptance criteria fixed. Choose the lowest budget that meets your quality bar without increasing retries or review time (Splunk, *Scaling Laws of AI Tokenomics*). Use different budgets for discovery (open-ended hunting needs room plus a stopping rule) and execution (well-defined steps should converge quickly).

## Sources

- OWASP Top 10 for LLM Applications, LLM10:2025 Unbounded Consumption: <https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/>
- MCP SEP-1576, *Mitigating Token Bloat in MCP*: <https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576>
- OpenAI Batch API FAQ: <https://help.openai.com/en/articles/9197833-batch-api-faq>
- Gemini optimization (Batch, Flex): <https://ai.google.dev/gemini-api/docs/optimization>
- Splunk, *Scaling Laws of AI Tokenomics*: <https://www.splunk.com/en_us/blog/artificial-intelligence/scaling-laws-of-ai-tokenomics.html>
