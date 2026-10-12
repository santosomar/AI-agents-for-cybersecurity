# 7. Choosing Models with the Cyber Index

General-purpose leaderboards tell you little about how a model performs as a *defensive security agent*, or what it costs to get there. The **Artificial Analysis Cyber Index** is an independent, cost-aware benchmark built for exactly that: agents that discover, reproduce, and patch vulnerabilities.

Live results: <https://artificialanalysis.ai/evaluations/artificial-analysis-cyber-index>

## Three evaluations for a defensive agentic loop

| | CWE-Bench-AA | DeepsecBench-AA | CyberGym-E2E-AA |
|---|---|---|---|
| **From** | Collinear AI | Vercel | Berkeley RDI |
| **Task** | Audit a real open-source repository for a described weakness, then patch it | Review application code and report every vulnerability you can confirm | Find a memory-safety bug in C/C++, write a crashing input, and patch it without breaking tests |
| **Size** | 120 held-out tasks across all ten OWASP Top 10 (2025) categories; C/C++, Go, Java, JS/TS, Python, Rust | Private set, scored against an expert-verified golden set | 131 tasks, one per project (from the 920-instance CyberGym-E2E dataset), such as FFmpeg and CPython |
| **Scoring** | Deterministic verifier (exploit blocked *and* legitimate behavior still works), pass@1 | LLM judge matches findings to the golden set; median **F2** of 3 runs | Staged execution checks (sanitizer crash, then patch, then functionality tests), pass@1 |
| **Covers** | Discover → patch | Discover | Discover → reproduce → patch |

The index is the **equally weighted average** of the three scores on a 0–100 scale. Every model runs on the same open-source agent harness (**Stirrup**) in an isolated sandbox with no internet access, so differences reflect the model, not the vendor's agent product.

### Why F2 for DeepsecBench

\[
F_2 = \frac{5 \cdot P \cdot R}{4P + R}
\]

F2 weights recall (finding everything) four times as heavily as precision (not reporting false positives). That matches how security teams actually feel: a missed vulnerability is worse than a false positive a reviewer has to dismiss. Keep in mind that every false positive is still review time, which is the people term in [cost per outcome](06_cost_per_outcome.md).

## Reading the chart

The index chart shows two things per model:

- **Successes** (solid bar): the index score
- **Safety blocks** (hatched bar): the share of tasks where the model refused

Refusals **score zero** but are reported separately, so you can tell a model that tried and failed from one that declined. In the October 2026 results, several models show safety blocks on roughly a third to well over half of these *defensive* tasks. For a security team, a refusal is not free: the work goes back to a person.

## Turning scores into decisions

A benchmark score is an acceptance rate on someone else's tasks. Combine it with cost to get a first estimate of cost per outcome, then confirm it on your own tasks.

1. **Shortlist by capability on the sub-benchmark that matches your work.** For patching web applications, CWE-Bench-AA matters most. For code review, DeepsecBench-AA. For native code, CyberGym-E2E-AA.
2. **Check the refusal rate.** A high safety-block rate on defensive work is a hard operational cost. If your workflows include exploit reproduction or malware analysis, test refusal behavior directly. Some providers offer trusted-access programs for verified security teams.
3. **Compute cost to clear a backlog, not cost per solved task.** `04_cost_per_outcome.py` shows why. A cheaper model can look better per solved task, yet cost more overall because the tasks it does not solve become human work:

   | Model (illustrative) | Run cost (120 tasks) | Pass | Refuse | $/solved | Cost to clear all 120 |
   |---|---:|---:|---:|---:|---:|
   | A (frontier) | $260 | 55% | 0% | $3.94 | **$4,108** |
   | B (mid-tier) | $70 | 37% | 0% | **$1.58** | $5,457 |
   | C (cheap, cautious) | $25 | 13% | 57% | $1.60 | $5,839 |

4. **Build your own golden set.** Take 30–100 past tickets, findings, or incidents with known-good outcomes. Replay them through each candidate on your harness and tools. Record acceptance, review minutes, refusals, and cost. This is the only number that should drive the final decision.
5. **Route.** Use the benchmark winner for the hard steps (patching, exploitability) and cheaper models for the steps where they match its acceptance rate.

## Limits of any benchmark

- **Harness matters.** Scores on Stirrup will differ from scores in a vendor's own agent (Codex, Claude Code, and so on), which may add tools, retries, or longer budgets.
- **pass@1 is a single attempt.** In production you may allow retries, which raises acceptance and cost together.
- **Private sets help, but not forever.** Held-out tasks reduce contamination. Re-check results as models and the index are updated.
- **Defensive capability is dual-use.** The same skills that find and patch bugs can find and exploit them. Pair capable models with scope controls, sandboxing, and human approval for anything that touches systems you do not own.

## Sources

- Artificial Analysis Cyber Index: <https://artificialanalysis.ai/evaluations/artificial-analysis-cyber-index>
- Cyber Index methodology v1.0: <https://artificialanalysis.ai/methodology/cyber-index>
- Launch article, *Announcing the Artificial Analysis Cyber Index Alliance*: <https://artificialanalysis.ai/articles/artificial-analysis-cyber-index>
- CWE-Bench-AA: <https://artificialanalysis.ai/evaluations/cwe-bench-aa>
- DeepsecBench-AA: <https://artificialanalysis.ai/evaluations/deepsecbench-aa>
