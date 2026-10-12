# 1. How Tokens Are Billed

Before you can cut an agent's bill, you need to know what is on it. Every major provider bills the same few things, in the same unit: **US dollars per million tokens (USD/MTok)**.

## What a token is

A token is a chunk of text produced by the model's tokenizer: roughly ¾ of an English word, or about 4 characters. Code, JSON, IP addresses, hashes, and base64 tokenize much less efficiently than prose. A SHA-256 hash is 64 characters and about 33 tokens with `o200k_base`, roughly double what 64 characters of English prose would cost. Security data is token-dense, so you should measure it rather than estimate it:

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")   # GPT-5.x / GPT-6.x family
print(len(enc.encode(open("nmap_output.txt").read())))
```

Different model families use different tokenizers, so the same text costs a different number of tokens on Claude or Gemini. Use each provider's token-counting endpoint, or the `usage` object in the response, when you need exact numbers.

## The lines on the bill

| Line | What it is | Typical price relative to input |
|------|-----------|-------------------------------|
| **Input** | Everything you send: system prompt, tool schemas, history, tool results, the new message | 1× |
| **Cached input** (cache read) | Input tokens that match a prefix the provider already processed | 0.025×–0.1× |
| **Cache write** | Input tokens stored in the cache for later reuse | 1×–2× (provider and TTL dependent) |
| **Output** | Tokens the model generates, **including hidden reasoning/thinking tokens** | 4×–6× |
| **Tool fees** | Hosted web search, file search, code interpreter, and similar | Per call or per GB, billed separately |

Two consequences matter for agents:

1. **Output is expensive per token, but input dominates volume.** An agent call might read 20,000 tokens and write 500. Even at 5× the price, output is a small share of the bill. Input is where context management pays off.
2. **Reasoning tokens are billed as output, even though you never see them.** A "high effort" setting can multiply output tokens by 5–20× on hard prompts. Tune effort per step: use high effort for exploitability analysis, and low effort for IOC extraction.

## Service tiers

The same model is sold at different prices depending on how fast you need the answer. The tier multiplier applies to **every** line of the request, including cached and cache-write tokens.

| Tier | Multiplier | Latency | Use for |
|------|-----------|---------|---------|
| Batch | 0.5× | Up to 24 hours, asynchronous | Backlogs, nightly re-scoring, evals |
| Flex (OpenAI, Gemini) | 0.5× | Synchronous but best-effort; may be slower or shed | Non-urgent pipelines |
| Standard | 1× | Seconds | Interactive agents |
| Priority / Fast mode | ~1.75×–2× | Lowest, most reliable | User-facing, latency-critical paths |

## Long-context pricing

Long prompts can cost more per token, not just more in total:

- **OpenAI:** once a request's input passes **272K tokens**, the whole request is billed at long-context rates (2× input, 1.5× output on GPT-6.x).
- **Google Gemini 3.1 Pro:** prompts over **200K tokens** are billed at 2× input and 1.5× output.

Caching does not reduce the token *count*, so it cannot pull a request back under a long-context threshold. Only compaction can.

## October 2026 price snapshot

Standard tier, short context, USD per million tokens. This is the same data as [`pricing.yaml`](../pricing.yaml).

| Model | Input | Cached input | Cache write | Output |
|-------|------:|------------:|-----------:|-------:|
| gpt-6-astra | 10.00 | 1.00 | 12.50 | 50.00 |
| gpt-6.1-sol | 2.00 | 0.10 | 2.50 | 10.00 |
| gpt-6-sol | 2.00 | 0.20 | 2.50 | 10.00 |
| gpt-6-luna | 0.10 | 0.01 | 0.125 | 0.50 |
| claude-fable-5.1 | 10.00 | 0.25 | 12.50 (5 min) / 20.00 (1 h) | 50.00 |
| claude-opus-5 | 5.00 | 0.50 | 6.25 / 10.00 | 25.00 |
| claude-sonnet-5 | 2.00 | 0.20 | 2.50 / 4.00 | 10.00 |
| claude-haiku-4.5 | 1.00 | 0.10 | 1.25 / 2.00 | 5.00 |
| gemini-3.8-flash | 0.75 | 0.075 | 0.75 (implicit) | 3.75 |
| gemini-3.1-pro-preview | 2.00 | 0.20 | 2.00 (implicit) | 12.00 |

The spread between the cheapest and most expensive input rate is **100×** (gpt-6-luna vs gpt-6-astra). That spread is what makes model routing worthwhile (see [write-up 4](04_model_routing.md)).

Gemini Flash prices above are promotional through December 31, 2026, and double on January 1, 2027. Gemini explicit caches also charge storage per million tokens per hour.

## Reading the usage object

Every response tells you what you were billed for. Log it on every call:

| Provider | Input | Cached | Cache write | Output |
|----------|-------|--------|-------------|--------|
| OpenAI Responses API | `usage.input_tokens` | `usage.input_tokens_details.cached_tokens` | `usage.input_tokens_details.cache_write_tokens` | `usage.output_tokens` (reasoning in `output_tokens_details.reasoning_tokens`) |
| Anthropic Messages API | `usage.input_tokens` (uncached only) | `usage.cache_read_input_tokens` | `usage.cache_creation_input_tokens` | `usage.output_tokens` |
| Gemini | `usage_metadata.prompt_token_count` | `usage_metadata.cached_content_token_count` | n/a | `usage_metadata.candidates_token_count` (+ `thoughts_token_count`) |
| LangChain (any provider) | `message.usage_metadata["input_tokens"]` | `["input_token_details"]["cache_read"]` | `["input_token_details"]["cache_creation"]` | `["output_tokens"]` |

Watch the semantics. In OpenAI's usage object, `input_tokens` is the total and cached tokens are a subset of it. In Anthropic's, `input_tokens` counts only the uncached remainder. `token_math.request_cost()` follows the OpenAI convention.

## Stateful APIs do not make context free

OpenAI's `previous_response_id`, Gemini's `previous_interaction_id`, and similar "stateful" features save you from re-uploading the history, but the model still processes it. **Prior turns are still billed as input tokens on every call** (at cached rates when they hit the cache). The compounding described in [write-up 2](02_context_compounding_and_compaction.md) still applies.

## Sources

- OpenAI API pricing: <https://developers.openai.com/api/docs/pricing>
- Anthropic pricing and prompt caching: <https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching>
- Gemini API pricing: <https://ai.google.dev/gemini-api/docs/pricing>
- Gemini optimization (Flex, Batch, Priority, caching): <https://ai.google.dev/gemini-api/docs/optimization>
