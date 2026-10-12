# Hermes Agent

> A self-improving agent from Nous Research. After it completes a non-trivial task, it writes the workflow down as a reusable **skill**, then reloads and refines that skill the next time a similar task appears. The longer you use it, the more of your procedures it learns.

## What it is

| | |
|---|---|
| **From** | [Nous Research](https://nousresearch.com/) |
| **Repo** | [`NousResearch/hermes-agent`](https://github.com/NousResearch/hermes-agent) |
| **Interfaces** | Full TUI/CLI, plus one gateway for Telegram, Discord, Slack, WhatsApp, Signal, and Home Assistant |
| **Terminal backends** | Local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox |
| **Skills** | Markdown `SKILL.md` files under `~/.hermes/skills/`, compatible with the [agentskills.io](https://agentskills.io) standard; shareable via a Skills Hub |
| **Memory** | Agent-curated memory, FTS5 search over past sessions, Honcho user modeling |
| **Other** | Built-in cron scheduler, parallel sub-agents, MCP client, 40+ tools |

### The learning loop

1. **Observe.** Tool calls, decisions, errors, and your corrections are tracked during a session.
2. **Distill.** A background review agent reads the finished session. If it shows a non-trivial workflow, a fix, or a correction, it calls `skill_manage` to write or patch a `SKILL.md`. **No human approval is required by default.**
3. **Reuse.** Only skill names and descriptions sit in context; the full skill loads when a task matches.
4. **Refine.** If a loaded skill fails or a better path is found, Hermes patches the skill mid-task.

A companion project, [`hermes-agent-self-evolution`](https://github.com/NousResearch/hermes-agent-self-evolution), uses DSPy + GEPA to evolve skills offline from execution traces.

## Where it helps a security team

- **Capturing tribal knowledge.** Investigations that a senior analyst walks through once (triage a phishing report, pivot from an IP in the SIEM, enrich a hash) can become reviewable runbooks in plain Markdown. Because skills are files, you can put them in Git and review them like code.
- **Recurring, unattended reports.** The cron scheduler can produce a daily vulnerability digest, a weekly patch-compliance summary, or a nightly "new internet-facing assets" diff and post it to Slack or Telegram.
- **Isolated execution by design.** Running tools through the Docker, Modal, or Daytona backends keeps shell activity off the analyst's laptop. Sandboxes hibernate when idle, which keeps costs low.
- **Parallel enrichment.** Sub-agents can fan out across a list of indicators and merge the results.
- **Research and red-team labs.** The self-modifying skill system is an excellent teaching target for *persistent* prompt injection and memory poisoning.

## Where it should stay out

- **Unreviewed self-modification in production workflows.** A skill learned from a session that contained attacker-controlled text (a log line, a ticket, a web page) can carry that influence into every future run. Auto-written skills must be reviewed before they touch anything important.
- **Running directly on a host with secrets.** Hermes' own `SECURITY.md` is blunt: *"The only security boundary against an adversarial LLM is the operating system."* The approval gate, output redaction, and Skills Guard are explicitly **not** security boundaries.
- **Community skills you haven't read.** Skills can execute arbitrary Python at import time. A public report showed Skills Guard's regex scanner could be bypassed with dynamic imports to silently exfiltrate environment variables. Nous closed it as out of scope: reviewing third-party code is the operator's job.
- **Non-interactive modes over untrusted data.** Past issues showed batch and cron paths auto-approving dangerous commands, so a poisoned dataset or skill could reach the shell. These specific bugs were fixed, but the lesson stands: unattended runs plus untrusted input means no human is watching the approval gate.
- **Shared multi-user gateways holding privileged tokens.** As with OpenClaw, anyone who can message the gateway can steer the agent.
- **Memory that mixes trust levels.** Issues have shown framework-injected skill text being stored in memory as if the user had said it. Don't let one memory store serve both sensitive and public contexts.

## Hardening checklist

- [ ] Use a container or remote sandbox backend (Docker, Modal, Daytona), not `local`, for anything touching untrusted input
- [ ] Keep `~/.hermes/skills/` under version control and require review (pull request) for new or changed skills
- [ ] Read the Python and scripts of every third-party skill before install; check `~/.hermes/skills/.hub/audit.log`
- [ ] Keep command approval on for interactive sessions; give cron and batch jobs a minimal toolset and no production credentials
- [ ] Pair DMs on the messaging gateway; allowlist who can talk to it
- [ ] Separate memory/profile per trust domain
- [ ] Watch the [Hermes security advisories and issues](https://github.com/NousResearch/hermes-agent/security) (for example, CVE-2026-9367 in the dangerous-command detector)

## Sources

- [NousResearch/hermes-agent (GitHub)](https://github.com/NousResearch/hermes-agent)
- [Hermes `SECURITY.md`](https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md)
- [Hermes learning loop](https://hermes-agent.ai/features/learning-loop)
- [Inside Hermes Agent: how self-improving skills work](https://fp8.co/articles/Inside-Hermes-Agent-Self-Improving-Skill-Memory)
- [hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution)
- [Issue #35164: approval bypass in `batch_runner.py`](https://github.com/NousResearch/hermes-agent/issues/35164)
- [Issue #3968: cron prompt injection via skill content](https://github.com/NousResearch/hermes-agent/issues/3968)
- [Issue #7072: Skills Guard bypass via dynamic import](https://github.com/NousResearch/hermes-agent/issues/7072)
- [Issue #92036: auto-loaded skill bodies stored as user memory](https://github.com/NousResearch/hermes-agent/issues/92036)
