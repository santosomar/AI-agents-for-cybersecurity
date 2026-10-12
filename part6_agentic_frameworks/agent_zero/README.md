# Agent Zero

> A general-purpose agent that gets its own Linux computer. Agent Zero runs inside a Docker container built on **Kali Linux**, where it has root, a real terminal, a browser, an XFCE desktop, and hundreds of pre-installed tools. It uses the operating system itself as its main tool.

## What it is

| | |
|---|---|
| **From** | agent0ai community |
| **Repo** | [`agent0ai/agent-zero`](https://github.com/agent0ai/agent-zero) |
| **Runtime** | Docker container (Kali Linux base), with a Web UI |
| **Quick start** | `docker run -p 80:80 -v a0_usr:/a0/usr agent0ai/agent-zero` |
| **Inside the container** | Root access, `apt`/`pip`/`npm`, Python, Node.js, Bash, networking, Kali tooling (`nmap`, `wireshark`, and more) |
| **Features** | Multi-agent (agents spawn subordinate agents), long-term memory, skills, plugin hub (with an AI-driven plugin scan), browser agent with DOM annotation, desktop, "Time Travel" file snapshots |
| **Host bridge** | Optional **A0 CLI Connector** that grants read/write and remote code execution on a *host* machine |

The design philosophy is transparency and customization: prompts, tools, and behaviors live in editable files, and the agent installs whatever it needs on the fly.

## Where it helps a security team

- **Disposable offensive-security lab.** Because it ships on Kali, it is a natural fit for authorized penetration-testing practice, CTFs, and red-team training against lab targets (for example, HackTheBox, DVWA, or your own range).
- **Recon and enumeration helper (authorized scope only).** It can chain `nmap`, `whois`, DNS tools, and web fetches, then summarize the findings. This pairs well with the nmap examples in Part 5.
- **Malware and artifact triage sandbox.** Static analysis of suspicious files, decoding obfuscated scripts, or parsing logs inside a throwaway container, with snapshots to roll back.
- **Tool prototyping.** Ask it to write and test a parser, a detection script, or a quick PoC; the container is a safe place for code to run.
- **Teaching multi-agent delegation.** The superior/subordinate agent hierarchy is easy to observe in the UI.

## Where it should stay out

- **Your host machine.** The container is the safety boundary. The A0 CLI Connector with read/write plus remote code execution, broad volume mounts (especially `$HOME`), or the Docker socket mounted inside the container all remove that boundary. Agent Zero's README itself says not to mount your home directory unless you understand the risk.
- **Networks you are not authorized to test.** A root shell with Kali tools and full network access will happily scan or exploit whatever the model decides is in scope. Put it on an isolated network segment with egress controls, never on a flat corporate LAN.
- **Holding real credentials.** Community reports in 2026 included plaintext secrets leaking into the LLM system prompt (issue #1107) and API keys echoed into error logs (issue #1071). Assume anything you give it can end up in the model provider's logs.
- **Internet-exposed instances.** The Web UI and the built-in tunnel feature must have authentication set first. CVE-2026-30624 (Agent Zero 0.9.8) allowed remote code execution through attacker-supplied external MCP server configs. An independent 2026 report counted multiple critical and high findings, many inherited from dependencies.
- **Production change-making.** Don't let it touch production servers, cloud consoles, or identity systems. It is a lab tool, not an operator.
- **Untrusted plugins and browser extensions.** The AI-based plugin scan is a convenience, not a guarantee.

## Hardening checklist

- [ ] Run only in Docker or a VM, on an isolated network with egress filtering
- [ ] Mount a dedicated, empty work volume; never mount `$HOME`, `/`, or `/var/run/docker.sock`
- [ ] Leave the A0 CLI Connector disabled unless the target is itself a disposable machine
- [ ] Set Web UI username/password before enabling the tunnel; bind to localhost otherwise
- [ ] Use scoped, low-value API keys with spend limits; rotate them often
- [ ] Keep the image updated; track [Agent Zero issues and advisories](https://github.com/agent0ai/agent-zero/issues)
- [ ] Write the authorized scope (targets, time window) into the project instructions, and still verify every action against it
- [ ] Back up workspaces; use Time Travel snapshots for rollback, but don't rely on them as a security control

## Sources

- [agent0ai/agent-zero (GitHub)](https://github.com/agent0ai/agent-zero)
- [Agent Zero installation docs](https://github.com/agent0ai/agent-zero/blob/main/docs/setup/installation.md)
- [Agent Zero capabilities (knowledge base)](https://github.com/agent0ai/agent-zero/blob/2d95cd9f/knowledge/main/about/capabilities.md)
- [I run on Kali Linux. Here's what that means](https://www.agent-zero.ai/p/articles/agent-zero-kali-linux/)
- [CVE-2026-30624: Agent Zero command injection](https://rdintel.com/cve/CVE-2026-30624)
- [Issue #1107: secrets exposed in LLM system prompts](https://github.com/agent0ai/agent-zero/issues/1107)
- [Issue #1071: API key leaks in error logs](https://github.com/agent0ai/agent-zero/issues/1071)
- [Issue #1074: command injection via project name in SSH cwd](https://github.com/agent0ai/agent-zero/issues/1074)
- [Issue #1592: security posture report](https://github.com/agent0ai/agent-zero/issues/1592)
