# Paperclip

> A control plane for a "company" of AI agents. Paperclip doesn't run agents itself. It gives them an org chart, goals, tasks, budgets, approval gates, and an audit trail, and it wakes them up on a heartbeat. If an agent can receive a heartbeat, it can be "hired."

## What it is

| | |
|---|---|
| **From** | paperclipai |
| **Repo** | [`paperclipai/paperclip`](https://github.com/paperclipai/paperclip) |
| **Stack** | Node.js server + React UI; self-hosted, no Paperclip account required |
| **Runs on** | Laptop, Docker, or a server |
| **Agents it orchestrates** | Claude Code, Codex, Cursor/Gemini CLIs, OpenClaw (via webhook), shell scripts, any HTTP agent, plus adapter plugins |
| **Core objects** | Companies → org chart (CEO, managers, workers) → goals → tasks/comments → heartbeats → budgets → approvals |
| **Multi-tenancy** | One instance can host many companies with data isolation |

Paperclip is explicit about what it is **not**: not a chatbot, not an agent framework, not a workflow builder, and not a code-review tool. It is the management layer above agents.

### Built-in governance

- **Deployment modes:** `local_trusted` (loopback only, no login) or `authenticated` (login required; `private` for LAN/VPN/Tailscale, `public` for internet-facing with stricter checks)
- **Agent credentials:** per-agent API keys (stored as hashes, shown once) or short-lived JWTs, each scoped to one agent and one company
- **Approvals:** hiring a new agent or adopting a CEO strategy requires board (human) approval; agents cannot approve their own requests
- **Budgets:** per-agent token "salaries"; warning at 80%, hard stop and pause at 100%
- **Secrets:** encrypted at rest (AES-256-GCM), referenced as `$secret:name`, with an optional strict mode that blocks inline secrets
- **Audit:** every mutating action is logged and attributed to an actor

## Where it helps a security team

- **Governing an agent fleet.** If your team already runs several coding or ops agents, Paperclip gives you one place to see who is working on what, what it costs, and what it is waiting on.
- **Spend control.** Hard budget caps stop a runaway agent loop from burning thousands of dollars in API calls, which is a real availability and financial risk.
- **Human-in-the-loop by default.** Approval gates for new agents and strategies map naturally to change management: no new autonomous worker gets credentials without a human sign-off.
- **Accountability and forensics.** Goal-linked tasks and an attributed activity log help answer "why did this agent do that?" during incident review.
- **Modeling a security program.** Small teams can experiment with a "virtual SOC" org chart (a triage agent, an enrichment agent, a reporting agent, a human "board"), keeping every action tracked and pausable.
- **Kill switch.** Board users can pause, resume, or terminate any agent immediately.

## Where it should stay out

- **`local_trusted` on anything but your own laptop.** That mode treats every request as a full-trust board actor with no login. Never bind it beyond `127.0.0.1` or put it behind a tunnel.
- **Being mistaken for a sandbox.** Paperclip orchestrates; the agents run elsewhere with whatever permissions *their* runtime has. A Claude Code or OpenClaw worker hired by Paperclip is only as safe as its own sandbox and credentials.
- **"Zero-human" operation of security controls.** The project's framing is autonomous companies running 24/7. Don't apply that to incident response actions, firewall or IAM changes, or customer communications without human approval on each consequential step.
- **Treating agent output as verified.** Task comments and "done" statuses are agent claims. Verify findings, especially anything that closes a vulnerability or an incident ticket.
- **Over-sharing context across agents.** By default an agent key can read *all tasks in the company*. Don't put sensitive incident details in a company that also hosts lower-trust agents; use separate companies.
- **Public stdio MCP runtimes.** In `authenticated/public` mode, local stdio MCP runtimes fail closed for a reason; prefer remote HTTP MCP over trusting the server host to supervise arbitrary processes.

## Hardening checklist

- [ ] Use `authenticated` mode for anything beyond a single local operator; `public` only behind a reverse proxy with TLS
- [ ] Turn on secrets strict mode; store keys as `$secret:` references, never inline
- [ ] Keep rate limiting on (it defaults off in `private` mode)
- [ ] Separate companies by trust level (for example, "IR-sensitive" vs. "general automation")
- [ ] Set conservative budgets per agent; review the costs page weekly
- [ ] Rotate agent API keys and review `lastUsedAt` for unused keys
- [ ] Harden each worker agent independently (see the OpenClaw, Hermes, and OpenHands folders)
- [ ] Export the activity log to your SIEM

## Sources

- [paperclipai/paperclip (GitHub)](https://github.com/paperclipai/paperclip)
- [What is Paperclip?](https://paperclipai-paperclip.mintlify.app/introduction)
- [`doc/PRODUCT.md`](https://github.com/paperclipai/paperclip/blob/master/doc/PRODUCT.md)
- [`doc/DEPLOYMENT-MODES.md`](https://github.com/paperclipai/paperclip/blob/master/doc/DEPLOYMENT-MODES.md)
- [Paperclip security docs](https://paperclipai-paperclip.mintlify.app/deployment/security)
- [API authentication reference](https://docs.paperclip.ing/reference/api/authentication.md)
- [Approvals guide](https://docs.paperclip.ing/guides/day-to-day/approvals/)
