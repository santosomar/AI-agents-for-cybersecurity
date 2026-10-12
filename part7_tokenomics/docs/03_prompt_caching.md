# 3. Prompt Caching

Prompt caching is the single biggest discount available to agents, because agents re-send the same prefix on every call.

## How it works

When a model processes a prompt, it builds internal state (the key/value cache) for every token. If the next request starts with **exactly** the same tokens, the provider can reuse that state instead of recomputing it, and bills those tokens at a steep discount. Reuse is decided on the **prefix**: matching stops at the first token that differs.

```
call 1: [ system | tools | runbook ][ alert 1 ]     -> cache write for the prefix
call 2: [ system | tools | runbook ][ alert 2 ]     -> cache read for the prefix
call 3: [ 2026-10-11T17:02Z | system | tools ... ]  -> nothing matches, full price
```

## Provider mechanics (October 2026)

| | OpenAI (GPT-5.6 and later) | Anthropic | Google Gemini |
|---|---|---|---|
| How it is enabled | Automatic | Automatic (top-level `cache_control`) or explicit breakpoints (up to 4) | Implicit (automatic) on Gemini 2.5+; explicit `CachedContent` objects |
| Cache read | 0.1× input (0.05× on GPT-6.1 Sol) | 0.1× input (0.025× on Claude Fable 5.1 / Mythos 5.1) | 0.1× input |
| Cache write | 1.25× input | 1.25× (5-minute TTL) or 2× (1-hour TTL) | 1× (implicit); explicit adds storage per MTok-hour |
| Lifetime | At least 30 minutes after last use, up to 24 h; `prompt_cache_options.ttl` | 5 minutes default, or `"ttl": "1h"`; refreshed on every hit | Implicit: minutes to hours, always deleted within 24 h; explicit: you set the TTL |
| Minimum prefix | 1,024 tokens | Model-dependent (about 1,024–4,096) | 2,048–4,096 tokens, model-dependent |
| Usage fields | `input_tokens_details.cached_tokens`, `.cache_write_tokens` | `cache_read_input_tokens`, `cache_creation_input_tokens` | `cached_content_token_count` |

All of these multipliers **stack** with the Batch discount. A cache read inside an OpenAI batch on GPT-6.1 Sol costs $0.05/MTok instead of the standard $2.00/MTok input rate.

## Break-even

Measured in multiples of the prefix's normal input cost:

| Calls | No cache | 1.25× write + 0.1× reads | 2× write + 0.1× reads |
|-----:|--------:|------------------------:|---------------------:|
| 1 | 1.00× | 1.25× | 2.00× |
| 2 | 2.00× | **1.35×** | 2.10× |
| 3 | 3.00× | 1.45× | **2.20×** |
| 10 | 10.00× | 2.15× | 2.90× |

A 1.25× write pays for itself on the first reuse. A 2× write needs two. After that, every reuse is about 90% off.

## Match the TTL to your traffic

The TTL only helps if the next request arrives before the cache expires. `02_prompt_caching.py` prices 40 alerts on Claude Sonnet 5 with a 12k-token prefix:

| Gap between alerts | No cache | 5-minute TTL | 1-hour TTL |
|-------------------|--------:|------------:|----------:|
| 1–4 minutes | $1.20 | **$0.36** | $0.38 |
| 10–30 minutes | $1.20 | $1.44 | **$0.38** |
| 90 minutes | **$1.20** | $1.44 | $2.16 |

When requests arrive every few minutes, use the cheap 5-minute write. When there are long human-approval pauses, as is common in SOC workflows, the 5-minute cache expires every time: you pay the write premium on every call and never collect a read. Use the 1-hour TTL in that case. When gaps exceed the longest TTL, caching costs **more** than not caching.

## Prompt layout rules

1. **Static first, variable last.** System prompt, then tool definitions, then reference documents, then conversation history, then the new message.
2. **No timestamps, request IDs, or user names in the system prompt.** One changing token at the top invalidates everything below it. If the model needs the date, put it in the last message. `02_prompt_caching.py` shows that a timestamp at the top makes caching *more* expensive than no caching on providers that charge a write premium.
3. **Keep tool definitions stable and in a fixed order.** Adding, removing, or reordering a tool changes the prefix. Load tools deterministically, for example sorted by name.
4. **Serialize deterministically.** Python dict ordering, JSON whitespace, and random IDs in tool results all break matches. Use `json.dumps(..., sort_keys=True, separators=(",", ":"))` for anything that goes into a cached region.
5. **Compact rarely, in big steps** (see [write-up 2](02_context_compounding_and_compaction.md)), so the prefix stays stable for many calls between compactions.

## Measure it

Track the **token cache-hit rate** per workflow:

\[
\text{cache-hit rate} = \frac{\sum \text{cached tokens}}{\sum \text{input tokens}}
\]

A healthy agent loop often runs at 70–90%. A sudden drop almost always means someone changed the system prompt, the tool list, or the serialization. `03_live_cache_check.py` prints the real numbers from the OpenAI API:

```bash
uv run python part7_tokenomics/03_live_cache_check.py --model gpt-6-luna
```

## Security considerations

- **Keep secrets out of cached prefixes.** API keys, credentials, and customer data have no business in a system prompt anyway. In a cached prefix they also persist on provider infrastructure for the TTL.
- **Partition caches per tenant.** Research on prompt-caching side channels (for example, Gu et al., *Auditing Prompt Caching in Language Model APIs*, 2025) showed that a cache hit is measurably faster than a miss. If caches are shared across users, an attacker can probe whether a given prefix was recently sent. Providers now scope caches to an organization; inside a multi-tenant app, use a per-tenant `prompt_cache_key` (OpenAI) or tenant-specific prefixes so one customer's traffic never warms another's cache.
- **Watch for cache-busting abuse.** An attacker who can inject varying content near the top of your prompt (a user display name in the system prompt, for example) can force a cache miss on every call and multiply your cost. This is one more reason to keep untrusted input at the end of the prompt.
- **Data retention.** Extended retention (`24h`) keeps prompt state longer. Check that it is compatible with your data-handling commitments, especially for regulated data.

## Sources

- OpenAI prompt caching guide: <https://developers.openai.com/api/docs/guides/prompt-caching>
- Anthropic prompt caching: <https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching>
- Gemini context caching: <https://ai.google.dev/gemini-api/docs/caching>
- Vertex AI context caching: <https://cloud.google.com/blog/products/ai-machine-learning/vertex-ai-context-caching>
