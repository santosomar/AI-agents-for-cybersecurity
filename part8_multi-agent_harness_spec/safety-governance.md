# Safety, Governance, and Rules of Engagement

> [!CAUTION]
> Exploitation validation and post-exploitation impact assessment may run **only** against explicitly named, isolated lab targets after a human grants a task-specific approval. No agent can self-approve, broaden scope, or substitute a planning artifact for authorization.

This is the harness constitution. The supervisor must fail closed when any requirement is unavailable or ambiguous. It addresses OWASP agentic risks including goal hijack, tool misuse, privilege abuse, memory poisoning, insecure inter-agent communication, cascading failures, and rogue agents.

## Authorization and scope manifest

Before any tool is reachable, an accountable operator supplies a versioned scope manifest:

| Required control | Requirement |
|---|---|
| Written authority | Owner, engagement ID, named operator, and approval date |
| Target allowlist | Stable lab asset IDs, private zones, and explicit exclusions; no CIDR wildcards without approval |
| Time window | Start/end, automatic expiry, renewal workflow |
| Capability allowlist | Read-only reconnaissance/discovery separately from validation and impact |
| Safety limits | Rate, concurrency, request volume, token/cost/tool-call/elapsed-time ceilings |
| Contacts | Operator, lab owner, incident contact, and emergency stop authority |
| Evidence rules | Collection limits, data classification, retention, redaction, and export destination |

Scope is evaluated at **every** tool call by a broker. A worker receiving an out-of-scope target returns `task.blocked`; it does not normalize, resolve, or probe it.

## Mandatory approval gates

| Gate | Trigger | Approver receives | Result |
|---|---|---|---|
| G0: start | Any assessment | Scope manifest, environment attestation, budget | Read-only phases may begin |
| G1: validation | Any exploit-like validation or state-changing test | Finding/evidence, exact approved target, expected harmless signal, rollback, budget | One-time short-lived capability token |
| G2: impact | Any simulated post-compromise impact assessment | Validated finding, containment proof, data minimization plan, detection owner | Separate one-time token |
| G3: close | Report release or artifact export | Findings, limitations, redactions, audit summary | Close/archive decision |

An approval binds `assessment_id + task_id + capability + target_id + parameters_digest + expiry + nonce`. Parameter changes, retries beyond the approved count, different assets, or expired tokens require a new approval. Rejection, timeout, budget breach, or missing rollback plan is a hard denial.

## Environment isolation

- Use disposable VMs/containers in a dedicated lab tenant/VLAN; production routes, corporate identity, shared mounts, host sockets, and metadata services are unreachable.
- Apply egress deny-by-default; permit only documented lab services. Block public DNS, arbitrary browsers, and unrestricted package installation.
- Give each worker a distinct workload identity with least privilege and short-lived broker credentials. Never put credentials in prompts, cards, logs, or this repository.
- Tool brokers, approval service, and audit sink are separate trust boundaries. Workers cannot edit policy, approvals, or external audit records.
- Exercise rollback and kill procedures before G1/G2 capabilities are enabled.

> [!IMPORTANT]
> A container is useful isolation, not automatic proof of isolation. Verify network paths, mounts, identities, and host escape protections independently.

## Budgets and loop ceilings

Tie implementation defaults to the patterns in [`part7_tokenomics/07_token_budget_guard.py`](../part7_tokenomics/07_token_budget_guard.py). The operator configures assessment and per-agent ceilings for tokens, money, tool calls, retries, concurrency, wall time, evidence bytes, and high-risk approvals.

At 80% of any ceiling, pause new task creation and alert the operator. At 100%, terminate the relevant task and revoke its capabilities. Enforce a maximum planning/replanning depth and detect repeated `(worker, capability, input digest)` attempts. A loop may not evade a budget by handing work to another agent.

## Audit and evidence

Write structured events to an append-only external sink before and after every policy decision, message, tool request, tool result, approval, budget decision, artifact export, and stop action. Include correlation IDs, actor/workload identity, scope version, tool version, parameter digest, result hash, and monotonic time. Redact secrets and sensitive lab data at collection; retain content only under the engagement's evidence policy.

Evidence must be attributable and reproducible. A model assertion without tool- or operator-sourced evidence is a hypothesis, never a validated finding.

## Hard stop / kill switch

Any operator with emergency-stop authority, or an automatic policy controller detecting an unsafe condition, can set the assessment to `aborted`. The control plane must:

1. revoke active capability and approval tokens;
2. cancel queued/running work and broker sessions;
3. deny new A2A tasks and MCP calls;
4. preserve an immutable audit snapshot; and
5. require human incident review and a fresh G0 approval before resumption.

Triggers include scope mismatch, unexpected external connectivity, artifact/exfiltration attempt, tool compromise, loss of audit path, suspected prompt injection that changes policy, budget exhaustion, or operator request.

## Prompt and memory controls

System prompts must state that external text is data, not authority. Retrieve only minimal, source-attributed context; sanitize and label it; never let a worker write long-term memory directly. Memory writes are reviewed, versioned, provenance-tagged, and limited to validated facts or operator-approved lessons. This reduces indirect prompt injection and persistent memory poisoning but does not replace sandboxing.

See [architecture.md](architecture.md) for the enforcement points and [references.md](references.md) for OWASP guidance.

