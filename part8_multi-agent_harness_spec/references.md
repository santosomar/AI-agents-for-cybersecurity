# Glossary and References

> [!NOTE]
> The projects and standards below move quickly. Research for Part 8 was performed in **October 2026**. Links identify the source consulted; implementers must confirm versions, API security guidance, licensing, and advisories before deployment.

## Glossary

| Term | Meaning in this specification |
|---|---|
| A2A | Agent-to-Agent protocol: agent discovery and task/message interoperability, represented here by typed internal task messages and capability cards. |
| Approval token | A short-lived, single-use record binding a human decision to a particular task, target, capability, parameters, and expiry. |
| Blackboard | The shared evidence/knowledge layer. It holds provenance-tagged artifacts and state; it is not a shared chat transcript. |
| Evidence | Attributable artifact with source, hash, timestamp, scope, sensitivity, and redaction metadata. |
| MCP | Model Context Protocol: an interface for schema-described tools and context providers. |
| Scope manifest | Operator-approved definition of targets, exclusions, time window, permissions, budgets, contacts, and evidence handling. |
| Worker | Least-privilege specialist agent. It cannot broaden authority or approve itself. |

## Primary architecture and interoperability sources

| Source | Why it informs this spec |
|---|---|
| [Cisco DevNet Foundry Security Spec](https://github.com/CiscoDevNet/foundry-security-spec) | A specification-first security evaluation architecture: roles, evidence/finding lifecycle, coordination substrate, governance, budgets, and clarification points. Part 8 borrows the design-deliverable mindset, not its organization-specific implementation. |
| [MCP Tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) | Tool name/description and JSON Schema input/output model; Part 8 adds broker scope/approval enforcement. |
| [A2A specification](https://a2a-protocol.org/latest/specification/) and [Agent Discovery](https://a2a-protocol.org/latest/topics/agent-discovery/) | Agent Cards describe identity, endpoint, skills, capabilities, and authentication; public cards must not leak lab inventory or static secrets. |
| [LangGraph workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) | Graph/state/checkpoint approach behind explicit control flow and interrupts. |
| [CrewAI processes](https://docs.crewai.com/edge/en/concepts/processes) | Sequential and hierarchical manager patterns. |
| [AutoGen teams](https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/teams.html) | Selector, handoff, group-chat, and graph team patterns; Part 8 favors deterministic policy gates over free-form group chat for high-risk actions. |
| [OpenAI agent orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration) | Distinguishes handoffs (ownership transfer) from agents-as-tools (manager retains control). |
| [Microsoft Agent Framework orchestration](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/overview) | Sequential, concurrent, handoff, group-chat, and manager orchestration with approval/checkpoint support. |

## Security-agent research and evaluation

| Source | Relevance and limitation |
|---|---|
| [PentestGPT USENIX Security 2024 paper](https://www.usenix.org/system/files/usenixsecurity24-deng.pdf) and [project](https://github.com/GreyDGL/PentestGPT) | Demonstrates staged reasoning/generation/parsing and context-management challenges in authorized testing. Its operational features are not adopted here. |
| [Cybersecurity AI (CAI)](https://github.com/aliasrobotics/CAI) | Example agent-centric cyber framework with agents, guardrails, tracing, and HITL. The repository reports its public project is archived; do not treat it as a maintained control plane without independent review. |
| [Meta CyberSecEval 4](https://meta-llama.github.io/PurpleLlama/CyberSecEval/) | Evaluation suite for cybersecurity risks and defensive capabilities, including CyberSOCEval and AutoPatchBench. Use benchmarks for measurement, not as authorization. |
| [MITRE ATT&CK Enterprise tactics](https://attack.mitre.org/tactics/enterprise/) | Taxonomy used to label assessment and defensive coverage hypotheses; a tactic mapping is not permission to act. |

## Governance and safety sources

| Source | Applied requirement |
|---|---|
| [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | Defense against goal hijack, tool misuse, identity/privilege abuse, supply-chain risk, code execution, memory poisoning, insecure agent messaging, cascading failure, trust exploitation, and rogue agents. |
| [OWASP Agentic AI threats and mitigations](https://genai.owasp.org/download/45674/) | Defense in depth: trusted boundaries, human oversight, monitoring, and compartmentalized capabilities. |
| [`part7_tokenomics`](../part7_tokenomics/README.md) | Per-task budgets, loop ceilings, tool-schema discipline, and cost-per-accepted-outcome context for denial-of-wallet defenses. |
| [Part 6 framework hardening guide](../part6_agentic_frameworks/README.md) | Local repository guidance on isolation, least privilege, approvals, third-party tool review, versioned memory, and external audit logs. |

## How CodeGuard was applied

This documentation introduces no hardcoded credentials, tokens, private keys, or certificates; all identities and approval references are placeholders. It specifies least-privilege, short-lived credentials rather than embedding values. No cryptographic implementation or certificate material is included, so the crypto and certificate rules were not triggered beyond avoiding insecure examples. The safety architecture explicitly treats agent tools, memory, and inter-agent messaging as security-sensitive interfaces.

