# OpenClaw

> A personal AI assistant you message from WhatsApp, Telegram, Slack, Discord, and other chat apps. It runs as a gateway on your own machine and can actually *do* things: read and send email, manage your calendar, run commands, browse, and call tools.

## What it is

| | |
|---|---|
| **Creator** | Peter Steinberger (now at OpenAI); formerly known as *Clawdbot* and *Moltbot* |
| **Steward** | OpenClaw Foundation, an independent US 501(c)(3) (announced July 2026) |
| **License** | MIT; no enterprise edition, no paid tier |
| **Runs on** | macOS, Windows, Linux; state lives on your machine |
| **Models** | Bring your own: hosted APIs, subscriptions, gateways, or local models |
| **Extensibility** | Skills (`SKILL.md`) from the ClawHub marketplace, plugins, MCP |
| **Identity files** | `SOUL.md` (persona), `MEMORY.md` (long-term memory), `HEARTBEAT.md` (scheduled behavior) |

OpenClaw became one of the fastest-growing repositories in GitHub history. Its pitch is "the AI that really does things": instead of chatting in a browser tab, you message your agent the way you would message a colleague, and it acts on your behalf with your accounts.

**Trust model (important):** OpenClaw's default trust model is a *personal assistant for one operator*, not hostile multi-tenant isolation. Sandboxing and execution approvals are **off by default**.

## Where it helps a security team

- **On-call companion for an individual analyst.** Ask it from your phone to pull the latest alerts, summarize a ticket, check a CVE in the CISA KEV catalog, or look up an IP's reputation, then reply in the same chat thread.
- **Scheduled personal briefings.** Use heartbeats to deliver a morning digest: new advisories for your vendor list, overnight high-severity alerts, expiring certificates.
- **Glue for low-risk lookups.** Wrap read-only APIs (threat intel feeds, asset inventory, internal wiki search) as skills so analysts can query them in natural language.
- **Lab and training use.** A good way to teach prompt injection, skill supply-chain attacks, and memory poisoning on a deliberately vulnerable, isolated install. OpenClaw has a rich public advisory history to study.
- **Its own audit tooling.** `openclaw security audit --deep` flags risky configs such as shared-user ingress, token reuse, and overly broad agent-to-agent session visibility.

## Where it should stay out

- **Shared team or SOC bots.** The trust model assumes one operator. If several people (or a public group chat) can message the same instance, any of them can steer an agent that holds *your* credentials.
- **Anywhere near production credentials.** Don't give it cloud admin keys, domain admin, EDR/SIEM write access, or your primary email if it also reads untrusted content.
- **Reading untrusted input with tools enabled.** Email, web pages, and chat links are indirect prompt injection channels. The Cloud Security Alliance documented zero-click data exfiltration through messaging-app link previews being exploited in the wild.
- **Unvetted ClawHub skills.** Koi Security's "ClawHavoc" research found 341 malicious skills out of 2,857 in early February 2026, rising to 824+ as the registry grew past 10,700. Snyk's ToxicSkills study found critical issues in 13.4% of skills scanned. Payloads included credential stealers, reverse shells, and Atomic macOS Stealer.
- **Internet-exposed gateways.** CVE-2026-25253 (fixed in 2026.1.29) let a crafted `gatewayUrl` leak the gateway token and chain to full command execution with approvals turned off. Related CVEs cover SSH command injection (CVE-2026-25157), SSRF, path traversal, and prompt-injection-driven code execution.
- **Regulated data.** Don't point it at PHI, PCI, or classified data unless your compliance team has reviewed where the model provider sends that data.

## Hardening checklist

- [ ] Run the latest release; subscribe to [OpenClaw security advisories](https://github.com/openclaw/openclaw/security/advisories)
- [ ] Turn on sandboxing for all sessions and require execution approvals
- [ ] Keep the gateway bound to loopback; never expose it publicly
- [ ] Use a dedicated machine or VM and dedicated low-privilege accounts, not your daily-driver identity
- [ ] Restrict who can DM the agent (allowlist senders; no open groups)
- [ ] Install skills only after reading their code, not just `SKILL.md`; pin versions
- [ ] Treat `SOUL.md` / `MEMORY.md` as security-sensitive files: monitor and back them up, and diff for unexpected edits
- [ ] Run `openclaw security audit --deep` after every config change
- [ ] Use separate tokens for hooks and the gateway (the audit warns on reuse)

## Sources

- [OpenClaw website](https://openclaw.ai/)
- [Introducing the OpenClaw Foundation](https://openclaw.ai/blog/introducing-openclaw-foundation)
- [Why OpenClaw (docs)](https://docs.openclaw.ai/start/why-openclaw)
- [`openclaw security` CLI docs](https://docs.openclaw.ai/cli/security.md)
- [NVD: CVE-2026-25253](https://nvd.nist.gov/vuln/detail/CVE-2026-25253) · [Vulhub reproduction](https://github.com/vulhub/vulhub/blob/master/openclaw/CVE-2026-25253/README.md)
- [CSA research note: OpenClaw indirect prompt injection](https://labs.cloudsecurityalliance.org/research/csa-research-note-openclaw-indirect-prompt-injection-2026061/)
- [Snyk: ToxicSkills study of ClawHub](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/)
- [Sangfor: OpenClaw security risks](https://www.sangfor.com/blog/cybersecurity/openclaw-ai-agent-security-risks-2026)
- [Forbes: OpenAI hires OpenClaw creator](https://www.forbes.com/sites/ronschmelzer/2026/02/16/openai-hires-openclaw-creator-peter-steinberger-and-sets-up-foundation/)
