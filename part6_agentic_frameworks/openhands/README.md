# OpenHands

> An autonomous software engineer: give it an issue, get a pull request back. OpenHands (formerly **OpenDevin**) runs coding agents inside sandboxes and connects them to GitHub, GitLab, Bitbucket, Azure DevOps, Slack, and more.

## What it is

| | |
|---|---|
| **From** | The OpenHands project (formerly OpenDevin / All-Hands-AI) |
| **License** | MIT (open-source core); OpenHands Cloud and OpenHands Enterprise are commercial |
| **Repos** | [`OpenHands/OpenHands`](https://github.com/OpenHands/OpenHands) (Agent Canvas UI) · [`OpenHands/software-agent-sdk`](https://github.com/OpenHands/software-agent-sdk) (Python SDK + Agent Server) |
| **Interfaces** | GUI, CLI, Python SDK, REST/WebSocket Agent Server |
| **Where agents run** | Docker containers, VMs, your own infrastructure, or OpenHands Cloud |
| **Integrations** | Issue resolver (`fix-me` label or `@openhands-agent` mention → draft PR), Slack, Datadog, scheduled automations |
| **Models** | Model-agnostic, routes to 100+ providers |

### Built-in security analysis

The SDK classifies every agent action **before** it runs and lets a confirmation policy decide whether to ask a human:

- `LLMSecurityAnalyzer`: the model labels each tool call `LOW`, `MEDIUM`, `HIGH`, or `UNKNOWN`
- `PatternSecurityAnalyzer` and `PolicyRailSecurityAnalyzer`: deterministic, offline checks (fetch-to-exec, raw disk writes, catastrophic deletes)
- `EnsembleSecurityAnalyzer`: combines analyzers and takes the worst case
- `ConfirmRisky(threshold=...)`, `AlwaysConfirm`, `NeverConfirm`: confirmation policies

```python
from openhands.sdk.security import (
    ConfirmRisky,
    EnsembleSecurityAnalyzer,
    PatternSecurityAnalyzer,
    PolicyRailSecurityAnalyzer,
    SecurityRisk,
)

conversation.set_security_analyzer(
    EnsembleSecurityAnalyzer(
        analyzers=[PolicyRailSecurityAnalyzer(), PatternSecurityAnalyzer()]
    )
)
conversation.set_confirmation_policy(ConfirmRisky(threshold=SecurityRisk.MEDIUM))
```

You must set **both** the analyzer and the policy; setting an analyzer alone does not change confirmation behavior. Calling `conversation.execute_tool()` directly bypasses both.

## Where it helps a security team

- **Remediating vulnerability backlogs.** Point it at dependency-bump issues, SAST findings, or Dependabot alerts and get draft PRs with the fix and a test. Humans still review and merge.
- **Security fixes at scale.** Apply the same secure pattern across many repos: replace an insecure crypto call, add input validation, remove hardcoded secrets in favor of environment variables (see the CodeGuard rules in `.cursor/rules/`).
- **Writing detection and tooling code.** Sigma/YARA rule scaffolding, log parsers, SOAR integrations, and unit tests for them.
- **First-pass code review.** Ask it to respond to PR comments or review a diff for risky patterns, then confirm the findings yourself.
- **Building your own security agents.** The SDK gives you sandboxed execution, event-sourced history, and the security-analyzer hooks above. It's a solid base for custom, auditable agents.

## Where it should stay out

- **Merging its own PRs or pushing to protected branches.** Keep branch protection and required human review. An agent that resolves issues can also be prompt-injected by issue text.
- **Public repos where anyone can trigger it.** Issue bodies and comments are untrusted input. If a stranger can add the `fix-me` label or mention the agent, they can steer it toward exfiltrating CI secrets or planting a backdoor. Restrict triggers to maintainers.
- **CI runners with production secrets.** Run the resolver with a narrowly scoped token (contents and pull requests on the target repo only), and keep deploy keys and cloud credentials out of its environment.
- **Running directly on a laptop.** The project's own docs warn "directly on your laptop (be careful!)". Use the Docker or VM backends.
- **`NeverConfirm` on anything that matters.** Fully autonomous mode is for trusted, disposable environments. The LLM-based risk label is the model grading its own homework; add the deterministic analyzers too.
- **Security-critical design decisions.** Authentication flows, cryptography, and authorization logic need a human expert. Use OpenHands to implement a reviewed design, not to invent one.

## Hardening checklist

- [ ] Use sandboxed backends (Docker/VM/remote); follow `SELF_HOSTING.md` hardening
- [ ] Configure `EnsembleSecurityAnalyzer` + `ConfirmRisky` (consider `MEDIUM` for sensitive repos)
- [ ] Only maintainers can trigger the resolver; open draft PRs only
- [ ] Use fine-grained, repo-scoped tokens; no org-admin or deploy credentials
- [ ] Enforce branch protection, CODEOWNERS, and required reviews on agent PRs
- [ ] Run SAST, secret scanning, and dependency checks on every agent PR, same as for humans
- [ ] Log conversations; the SDK's event-sourced history makes post-incident review possible

## Sources

- [OpenHands website](https://www.openhands.dev/)
- [OpenHands/OpenHands (GitHub)](https://github.com/OpenHands/OpenHands)
- [OpenHands SDK security architecture](https://docs.openhands.dev/sdk/arch/security)
- [Security & action confirmation guide](https://docs.openhands.dev/sdk/guides/security)
- [Defense-in-depth security example](https://github.com/OpenHands/software-agent-sdk/blob/main/examples/01_standalone_sdk/47_defense_in_depth_security.py)
- [Issue resolver README](https://github.com/OpenHands/OpenHands/blob/1.6.0/openhands/resolver/README.md)
- [The OpenHands Software Agent SDK (arXiv 2511.03690)](https://arxiv.org/abs/2511.03690)
- [OpenHands Enterprise GitHub integration](https://docs.openhands.dev/enterprise/integrations/github)
