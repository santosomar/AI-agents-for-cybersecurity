# Part 6: Agentic Frameworks for Security Teams

Parts 1–5 of this repository show how to *build* agents from primitives (LangChain, LangGraph, CrewAI, MCP). Part 6 looks at six popular, ready-made agentic frameworks and asks three questions about each one:

1. **What is it?**
2. **Where does it help a security team?**
3. **Where should it stay out?**

## The six at a glance

| Agent | What it is | From | Where it runs |
|-------|-----------|------|---------------|
| [OpenClaw](openclaw/) | A personal assistant you message in your chat apps | Peter Steinberger; now the OpenClaw Foundation | A gateway on your own machine |
| [Hermes](hermes/) | A self-improving agent that saves workflows as skills | Nous Research | Your host, a container, or a cloud sandbox |
| [Agent Zero](agent_zero/) | A general-purpose agent with its own Linux computer | agent0ai community | A Docker container (Kali Linux) |
| [OpenHands](openhands/) | An autonomous software engineer: issue in, pull request out | OpenHands (formerly OpenDevin) | A Docker sandbox, or its cloud |
| [Paperclip](paperclip/) | A control plane for a "company" of agents | paperclipai | Laptop, Docker, or server |
| [Buzz](buzz/) | A shared workspace for people and agents | Block | A relay you host yourself |

## How they relate

These are not six competitors. They sit at different layers of the stack:

```
             ┌──────────────────────────────────────────────┐
Coordination │  Paperclip (org chart, budgets, approvals)   │
             │  Buzz (shared channels, identity, audit log) │
             └──────────────────────────────────────────────┘
                              │ assigns / mentions
             ┌──────────────────────────────────────────────┐
Workers      │  OpenClaw · Hermes · Agent Zero · OpenHands  │
             └──────────────────────────────────────────────┘
                              │ tools, shell, browser, APIs
             ┌──────────────────────────────────────────────┐
Environment  │  Your laptop · Docker · VM · cloud sandbox   │
             └──────────────────────────────────────────────┘
```

- **Worker agents** (OpenClaw, Hermes, Agent Zero, OpenHands) take actions: run shell commands, browse, write code, send messages.
- **Coordination layers** (Paperclip, Buzz) do not do the work themselves. They decide who works on what, keep a record, and put humans in the loop.

## Shared risks across all six

Every framework in this part gives an LLM the ability to act. The same threat classes show up in all of them:

| Risk | What it looks like |
|------|-------------------|
| Indirect prompt injection | A web page, email, issue comment, or chat message contains instructions the agent follows as if they came from you |
| Skill / plugin supply chain | Community "skills" or plugins run arbitrary code. ClawHub audits in 2026 found hundreds of malicious skills |
| Persistent memory poisoning | Memory files, learned skills, or identity files (`SOUL.md`, `MEMORY.md`) get rewritten so the agent misbehaves in *future* sessions |
| Over-broad credentials | The agent holds tokens for email, GitHub, cloud, or chat, so one bad action can reach everything those tokens reach |
| Exposed control surfaces | Web UIs and gateways bound to `0.0.0.0` or tunneled to the internet without authentication |
| Approval fatigue / fail-open defaults | Confirmation prompts disabled for convenience; non-interactive modes that auto-approve |

The [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/) and the CodeGuard rules in `.cursor/rules/` are good companions to this part.

## A rule of thumb

> The only real security boundary for an agent is the operating system and network around it. Approval prompts, regex scanners, and "safety" system prompts are helpful speed bumps, not walls.

Hermes Agent states this explicitly in its own `SECURITY.md`, and it applies equally to the other five frameworks. Run them in containers or VMs, give them the narrowest credentials that work, keep them off production by default, and log everything.

## Directory layout

```
part6_agentic_frameworks/
├── README.md        ← this file
├── openclaw/        ← personal chat-app assistant
├── hermes/          ← self-improving agent with skills
├── agent_zero/      ← agent with its own Kali Linux container
├── openhands/       ← autonomous software engineer
├── paperclip/       ← control plane for a company of agents
└── buzz/            ← shared human + agent workspace on Nostr
```

Each sub-directory has a `README.md` with the same structure: what it is, where it helps a security team, where it should stay out, a hardening checklist, and sources.

> **Note:** These projects move fast. Facts were researched in October 2026; check each project's docs and security advisories before deploying.
