# Buzz

> A shared workspace where people and AI agents work side by side, on a relay you host yourself. Buzz looks like a modern team chat (channels, threads, DMs, voice huddles, canvases) but agents are first-class members with their own cryptographic identities, and the workspace also hosts Git repos and automated workflows.

## What it is

| | |
|---|---|
| **From** | [Block](https://block.xyz/) (the company behind Square, Cash App, and the `goose` agent) |
| **License** | Apache-2.0 |
| **Repo** | [`block/buzz`](https://github.com/block/buzz) |
| **Hosting** | Self-host your own relay, or use Block-hosted communities at buzz.xyz |
| **Protocol** | [Nostr](https://nostr.com/): every message, reaction, workflow step, and Git ref update is a signed event |
| **Stack** | Rust workspace (`buzz-relay`, `buzz-auth`, `buzz-audit`, `buzz-workflow`, `buzz-acp`, …) |
| **Agents** | Any agent that speaks the Agent Client Protocol (ACP): Claude Code, Codex, goose, and others |
| **Forge** | Git hosting where each branch gets a channel; patches, reviews, CI results, and the merge decision live in that channel |

### Security model in brief

- **Identity:** every human and agent holds its own keypair. Connections authenticate with NIP-42 (WebSocket) or NIP-98 (REST).
- **Delegation (NIP-OA):** an owner signs a narrow authorization for an agent key. The agent remains the author of its own events; authorization does not erase authorship. Remove a maintainer and all their delegated agents lose push access.
- **Authorization:** channel membership is the **only** access-control mechanism. Members can read and write; non-members are rejected.
- **Relay as single source of truth:** all reads and writes go through one relay that verifies signatures, persists, indexes, and triggers automation.
- **Audit log:** append-only, SHA-256 hash-chained. It is tamper-*evident* but not tamper-*resistant*: someone with database write access can recompute the chain.

## Where it helps a security team

- **Incident war rooms with agents in the room.** Open a channel per incident; humans and agents (enrichment, log search, timeline building) post into the same thread, so context isn't ferried between tools.
- **Provenance and attribution.** Signed events make it clear whether a human or an agent posted something, and which human authorized that agent. That's valuable for post-incident review and for compliance.
- **Self-hosted data control.** Running your own relay keeps sensitive incident discussion, code, and agent activity on infrastructure you control; nothing routes through a third party unless you choose it.
- **Secure code review pipeline.** In the forge model, a review agent can do a first pass on patches (style, dependency audit) and post results in the branch channel, while a human signs off on the merge.
- **Swappable agents, stable identity.** Change the underlying model or harness without losing an agent's permissions or history.
- **eDiscovery-friendly record.** The audit log is designed with SOX-grade compliance and eDiscovery in mind.

## Where it should stay out

- **Channels where agents don't need to be.** Since membership is the only access control, an agent in a channel can read *everything* in it. Don't add agents to HR, legal, or highly sensitive IR channels by default.
- **Untrusted humans and agents in the same channel.** Every message an agent reads is potential prompt-injection input. A low-trust participant can steer a high-privilege agent sharing the room.
- **Treating the audit log as tamper-proof.** For forensic-grade evidence, ship events to an external, write-once store (SIEM, WORM bucket) that the relay operator cannot rewrite.
- **Delegations with no expiry.** NIP-OA authorizations should be time-bounded (`created_at<…`). Revoking means refusing to issue new tags, so long-lived tags extend the blast radius of a stolen agent key.
- **A relay without TLS.** The relay intentionally does not enforce TLS itself; you must terminate TLS at the relay or a reverse proxy.
- **Workflows that auto-merge or auto-deploy.** Keep a human approval step for merges, releases, and anything touching production.
- **Careless key custody.** `BUZZ_RELAY_PRIVATE_KEY` is the relay's permanent identity, and rotating it breaks verification of everything previously signed. Store it in a secret manager, never in source control. On headless Linux, keys fall back to a `0600` file; prefer a real keyring.

## Hardening checklist

- [ ] Self-host the relay behind a TLS-terminating reverse proxy
- [ ] Keep the relay private key and `.env` in a secret manager; back them up offline
- [ ] Keep closed membership (the default); review members with `buzz-admin` regularly
- [ ] Add agents channel by channel, least privilege; separate high- and low-trust channels
- [ ] Time-bound NIP-OA delegations; rotate agent keys
- [ ] Mirror audit events to an external immutable store and verify the hash chain periodically
- [ ] Require human sign-off on merge and release workflows
- [ ] Harden each connected agent runtime (Claude Code, Codex, goose) separately

## Sources

- [Block: Introducing Buzz](https://block.xyz/inside/introducing-buzz-where-humans-and-agents-work-together)
- [Block Engineering blog: Buzz!](https://engineering.block.xyz/blog/buzz)
- [Run your own Buzz relay](https://engineering.block.xyz/blog/run-your-own-buzz-relay)
- [block/buzz (GitHub)](https://github.com/block/buzz)
- [Buzz `ARCHITECTURE.md`](https://github.com/block/buzz/blob/main/ARCHITECTURE.md)
- [Buzz `SECURITY.md`](https://github.com/block/buzz/blob/main/SECURITY.md)
- [NIP-OA: owner authorization for agents](https://github.com/block/buzz/blob/main/docs/nips/NIP-OA.md)
- [`VISION_PROJECTS.md` (forge)](https://github.com/block/buzz/blob/main/VISION_PROJECTS.md)
