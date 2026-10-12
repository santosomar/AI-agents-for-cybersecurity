# 6. Cost per Outcome, Not Tokens

> An "expensive" model could be cheaper at the end. Cheap tokens that need a second look aren't cheap. Pay for the outcome, not the attempt. The cheapest model is the one your reviewers never have to double- or triple-check.

## The formula

\[
\text{cost per accepted fix} = \frac{\text{model} + \text{runtime} + \text{human review}}{\text{acceptance rate}}
\]

- **Model:** every token across every call the task made, including retries, subagents, and evals
- **Runtime:** sandboxes, scanners, CI minutes, vector databases, egress, and GPUs if you self-host
- **Human review:** share of answers reviewed × minutes per review × the reviewer's loaded hourly cost
- **Acceptance rate:** the share of attempts whose result is accepted (merged, closed, or acted on)

The numerator is Splunk's *cost per accepted task*. Dividing by the acceptance rate is this course's extension. If only 60% of attempts are accepted, you need on average 1 / 0.6 ≈ 1.67 attempts per good result, and you pay the full numerator for each one.

## The hidden term is people

Splunk's example: a SOC agent costs **$0.02** per task in tokens. 40% of its answers need 15 minutes of review at $30/hour.

\[
\$0.02 + 0.40 \times \frac{15}{60} \times \$30 = \$0.02 + \$3.00 = \$3.02 \text{ per answer}
\]

The token bill is under 1% of the real cost. In security engineering and vulnerability management, where triage and patch re-checking are the norm, review is usually the largest term by far.

## Why an expensive model can be cheaper

From `04_cost_per_outcome.py`, an illustrative patch-proposal task with a $95/hour engineer reviewing:

| | Small model | Frontier model |
|---|---:|---:|
| Model cost per attempt | $0.03 | $0.90 |
| Runtime | $0.05 | $0.05 |
| Share needing review | 60% × 20 min | 15% × 10 min |
| Review cost per attempt | $19.00 | $2.38 |
| **Cost per attempt** | $19.08 | $3.33 |
| Acceptance rate | 55% | 90% |
| **Cost per accepted fix** | **$34.69** | **$3.69** |

The frontier model's tokens cost 30× more, yet each accepted fix costs 9.4× less. This is not an argument for always using the biggest model. It is an argument for measuring at the level of the outcome, then routing cheaper models to the steps where they match the acceptance rate (see [write-up 4](04_model_routing.md)).

## Sensitivity

Cost per accepted fix for a $0.20 model call, a $95/hour reviewer, and 15-minute reviews:

| Review share | Accept 50% | Accept 70% | Accept 90% | Accept 99% |
|------------:|----------:|----------:|----------:|----------:|
| 0% | $0.40 | $0.29 | $0.22 | $0.20 |
| 10% | $5.15 | $3.68 | $2.86 | $2.60 |
| 25% | $12.28 | $8.77 | $6.82 | $6.20 |
| 50% | $24.15 | $17.25 | $13.42 | $12.20 |

Reading across a row, acceptance rate multiplies everything. Reading down a column, even 10% review dwarfs a $0.20 model call. **The fastest way to cut cost per outcome is usually to cut review time**, through better models, better evidence in the agent's answer (links, queries run, diffs), and better verifiers, not cheaper tokens.

## Where tokens go: five buckets

Splunk suggests sorting every token into one of five buckets to see which spend drove progress:

| Bucket | Examples | Question to ask |
|--------|----------|-----------------|
| Context | System prompt, tool schemas, re-sent history | Is this re-sent more than it needs to be? |
| Reasoning | Thinking tokens, planning | Does higher effort raise acceptance on this step? |
| Retrieval | RAG chunks, tool output | Is it summarized before it enters the context? |
| Coordination | Supervisor ↔ subagent messages, handoffs | Are agents passing conclusions or full transcripts? |
| Governance | Validators, judges, guardrails, review triggers | Is this budgeted deliberately, or invisible? |

Classify one week of calls and cut the largest overhead bucket first. Optimizing before you measure usually trims the wrong thing.

## Token spend has a productive middle

More compute helps only while accepted results improve faster than cost and review time. Splunk's procedure for finding the middle:

1. Replay representative tasks at several budgets (for example, low, medium, and high effort, or 50k, 150k, and 400k token caps).
2. Keep the model, tools, and acceptance criteria fixed.
3. Plot cost per accepted task for each budget.
4. Choose the lowest budget that meets your quality and risk requirement without pushing retries or review time up.

If repeated runs keep failing the same way, stop paying to rediscover the failure. Fix the shared prompt, tool, or retrieval instead.

## What to record per task

| Field | Why |
|-------|-----|
| Workflow / task type | Costs only compare within a workflow |
| Model(s) and tier used | For routing and tier decisions |
| Input, cached, cache-write, output, and reasoning tokens | The model term, and the cache-hit rate |
| Tool calls and runtime cost | The runtime term |
| Retries and escalations | Hidden multipliers |
| Reviewer minutes | The people term |
| Accepted? (and why not) | The denominator, and your error taxonomy |

## Security considerations

- **A wrong answer in security is not just a cost.** A false negative in triage, or a patch that passes tests but leaves the vulnerability exploitable, has a cost that never shows up in this formula. Weight acceptance by severity, and never let cost targets push critical decisions to unreviewed automation.
- **Review time is also a control.** Cutting review to zero improves the metric and removes your safety net. Reduce review time by giving reviewers better evidence, not by skipping review on high-impact actions.
- **Measure refusals.** A model that refuses legitimate defensive work (scanning your own assets, analyzing malware samples) sends that work back to people. Count refusals as non-accepted outcomes. See [write-up 7](07_cyber_index.md).

## Sources

- Splunk, *What is Agent Tokenomics?*: <https://www.splunk.com/en_us/blog/artificial-intelligence/what-is-agent-tokenomics.html>
- Splunk, *Scaling Laws of AI Tokenomics*: <https://www.splunk.com/en_us/blog/artificial-intelligence/scaling-laws-of-ai-tokenomics.html>
- Splunk Tokenomics / Agent Observability: <https://www.splunk.com/en_us/products/tokenomics.html>
