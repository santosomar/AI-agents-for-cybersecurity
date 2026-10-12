# 4. Model Routing

**Small model first. Escalate only when needed.**

Input prices span 100× within a single provider's lineup (gpt-6-luna at $0.10/MTok vs. gpt-6-astra at $10/MTok). Most of the tokens an agent processes are not hard reasoning. They are extraction, classification, summarization, and formatting. Routing those steps to a small model moves most of the token *volume* to the cheapest tier while the frontier model keeps the decisions that matter.

## Two patterns

**Router.** Decide up front which model handles a step, from the step's type or a cheap classifier's verdict. There is no extra call when the routing is right, but it needs a good predictor.

```
alert ──► classify intent ──► extract_iocs      ──► gpt-6-luna
                          ├─► triage_reasoning  ──► gpt-6.1-sol
                          └─► write_patch       ──► claude-opus-5.5
```

**Cascade.** Always try the cheap model, check the answer, and escalate if the check fails. No predictor is needed, but escalated tasks pay for both attempts.

```
task ──► small model ──► check ──pass──► done
                           └──fail──► large model ──► done
```

The check can be schema validation (does the output parse into the expected structure?), a confidence threshold, self-consistency across two samples, or a judge model.

## What routing is worth

`05_model_routing.py` prices one day of SOC agent work (about 3,600 calls):

| Step | Calls | Routed to | Routed cost | All on gpt-6-astra |
|------|------:|-----------|-----------:|-----------------:|
| extract_iocs | 1,200 | gpt-6-luna | $0.54 | $54.00 |
| summarize_logs | 900 | gpt-6-luna | $0.95 | $94.50 |
| classify_alert | 1,200 | gpt-6-luna | $0.33 | $33.00 |
| triage_reasoning | 300 | gpt-6.1-sol | $10.80 | $54.00 |
| write_patch | 20 | claude-opus-5 | $3.50 | $7.00 |
| exploitability | 5 | gpt-6-astra | $2.50 | $2.50 |
| **Total** | | | **$18.61** | **$245.00** |

76% of tokens go to the small model, and the routed bill is 8% of the all-frontier bill. Published research points the same way: RouteLLM (LMSYS, ICLR 2025) reported 85% cost reduction on MT-Bench while keeping 95% of GPT-4 quality, and FrugalGPT (Stanford) reported cascades matching the best single model at a fraction of the cost.

## The escalation trap

A cascade's cost per task is:

\[
\text{cost} = c_\text{small} + c_\text{check} + (1 - r)\cdot c_\text{large}
\]

where *r* is the share of tasks the small model resolves.

| Small model resolves | Cost vs. large-only |
|--------------------:|-------------------:|
| 90% | 15% |
| 70% | 35% |
| 50% | 55% |
| 20% | 85% |
| 0% | **105%** (paying for both) |

The failure is silent. A too-strict validator, a provider-side change in the small model's output format, or drift in your data can push escalations toward 100%, and you only find out from the invoice. **Monitor the escalation rate like an SLO** and alert on it.

The opposite failure is worse: a too-lenient check lets wrong answers through. Those come back as human review time and rework, which is the most expensive term in [cost per outcome](06_cost_per_outcome.md).

## How to decide which steps to move

Splunk's routing guidance is a good procedure:

1. Open the workflow with the highest token spend and list each step.
2. Pick three steps that currently run on a frontier model.
3. Replay a representative sample of those steps on a cheaper model, keeping tools, prompts, and acceptance criteria fixed.
4. Compare **acceptance rate, retry rate, review time, and total cost**.
5. Move a step only when cost per accepted task falls *and* no new failure mode appears that you cannot tolerate.

Good candidates in security workflows include IOC extraction, log and tool-output summarization, alert de-duplication, ticket formatting, translating natural language to SPL or KQL (validated by running the query), and first-pass classification. Keep these on a strong model: exploitability judgments, patch generation that a human will merge, containment decisions (isolate a host, disable an account), and anything that writes to production.

## Security considerations

- **Route by risk, not just difficulty.** A step that can trigger a destructive action deserves the most reliable model *and* a human approval gate, no matter how easy the task looks.
- **Small models are easier to prompt-inject.** Do not give a cheap model, which reads untrusted logs, emails, or web pages, access to high-impact tools. Let it extract and summarize. Let a stronger, tool-restricted step decide.
- **Routers are attack surface too.** If an attacker can influence the routing decision (for example, by stuffing a log line with words that make the classifier pick a weaker path), they can choose which model handles their input. Route on trusted metadata such as alert source and type, not on attacker-controlled text alone.
- **Keep routes in config.** Store the route table outside the code, version it, and review changes to it like any other security-relevant configuration.

## Sources

- Splunk, *How to Reduce Agent Cost by Model Routing*: <https://www.splunk.com/en_us/blog/artificial-intelligence/reduce-agent-cost-by-model-routing.html>
- Ong et al., *RouteLLM: Learning to Route LLMs with Preference Data* (ICLR 2025): <https://arxiv.org/abs/2406.18665>
- Chen, Zaharia, Zou, *FrugalGPT* (2023): <https://arxiv.org/abs/2305.05176>
- Dekoninck et al., *A Unified Approach to Routing and Cascading for LLMs* (ETH Zurich): <https://arxiv.org/abs/2410.10347>
