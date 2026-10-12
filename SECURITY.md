# Security Policy

This repository is educational material by [Omar Santos](https://www.linkedin.com/in/santosomar/): standalone Python examples and design notes used in Pearson trainings, video courses, O'Reilly events, and books. It is not a hosted service. A security report is about a defect in this repository that can harm someone who clones it and follows the documented labs.

> [!IMPORTANT]
> Report vulnerabilities privately through [GitHub Security Advisories](https://github.com/santosomar/AI-agents-for-cybersecurity/security/advisories/new). Do not open a public issue, pull request, or discussion for a security report.

## Supported versions

| Version | Supported |
| --- | --- |
| [`main`](https://github.com/santosomar/AI-agents-for-cybersecurity) | Yes |
| Other branches | No |
| Code printed in a book or shown in a recorded course | No. This repository is the current version. |

Fixes land on `main`. There are no versioned releases to patch separately.

## Reporting a vulnerability

Use the private advisory form:

**https://github.com/santosomar/AI-agents-for-cybersecurity/security/advisories/new**

Private vulnerability reporting is enabled for this repository. The form notifies the maintainer without making the report public.

Include:

- The path, and the commit on `main` if you have it
- Who is affected (a learner running a documented script, a contributor using the GitHub workflows, or both) and what they can be made to do
- Impact, such as credential exposure, a command the lab does not document, or a workflow that runs untrusted code with write access
- Steps to reproduce on a machine and targets you control
- Whether the issue is in first-party code, `uv.lock` / `pyproject.toml` as used by a named script, or `.github/workflows/`

Leave out:

- Live API keys, tokens, private keys, passwords, or `.env` contents. Name the file and line, then rotate the credential. Treat any secret that reached this public repository as compromised.
- Scan output, hostnames, or data from systems you do not own or lack written permission to test
- Exploit payloads, shellcode, or proof-of-concept code aimed at a third party. Describe the behavior and the class of input. A minimal local reproduction is enough.

The maintainer aims to acknowledge a complete report within 7 days and to share an initial assessment within 14 days. Issues that expose credentials, run commands a learner did not request, or compromise a GitHub workflow are handled first. There is no bug-bounty program. You will be credited in the advisory if you want to be.

## In scope

Defects in this repository, when they show up by following the documented examples:

- Secrets, tokens, private keys, or connection strings committed in source, history, or example data
- Scripts or MCP examples that send `OPENAI_API_KEY`, `SHODAN_API_KEY`, or other `.env` values somewhere other than the provider the lab names
- nmap, ethical-hacking, attack-surface, CrewAI, or MCP examples that contact hosts other than the operator-supplied target
- Retrieval, URL-analysis, or tool-output paths that treat untrusted text as instructions and then leak secrets or run commands the lab does not describe
- GitHub Actions or Dependabot configuration that can expose `GITHUB_TOKEN` or run untrusted code with more permission than the workflow needs
- A dependency vulnerability that a documented script actually reaches. Name the script and the dependency.
- Part 8 text that enables exploitation validation or post-exploitation impact by default, or that adds operational exploit procedures, payloads, credential harvesting, persistence, evasion, or lateral movement. Part 8 is a specification, not a service. Its [out-of-scope list](part8_multi-agent_harness_spec/README.md) and [safety rules](part8_multi-agent_harness_spec/safety-governance.md) are the baseline.

## Out of scope

- Testing systems you do not own or are not explicitly authorized to test. Stop. Do not send that output here.
- Requests for exploit code, payloads, credential harvesting, persistence, evasion, or lateral-movement procedures
- Vulnerabilities in third-party products (model providers, LangChain, nmap, Shodan, operating systems, browsers). Report those to the vendor. Report them here only when this repository's own usage creates a distinct fix.
- Model quality, hallucinations, or disagreements about course explanations. Open a normal GitHub issue.
- Scanner findings with no demonstrated effect on a documented example
- Part 6 and Part 8 as if they were running products. They are documentation.

## Using the examples

Run scanning, MCP, attack-surface, and ethical-hacking examples only against systems you own or are explicitly authorized to test, ideally in an isolated lab. Keep API keys in the environment or a local `.env` file. `.env` is gitignored; do not commit it.

Part 8 does not ship a scanner. Its validation and impact phases stay off unless a human grants a task-specific approval for a named lab target. Read [safety-governance.md](part8_multi-agent_harness_spec/safety-governance.md) before treating that specification as an implementation guide.

## Disclosure

Please give the maintainer time to fix or document the issue before any public write-up. When the impact is real, the maintainer will publish a GitHub Security Advisory and the fix on `main`. If you have already published details, say so in the report.

## Safe harbor

This policy covers good-faith research into this repository. If you follow it, avoid privacy violations and service disruption, and stay on systems you are allowed to test, the maintainer will not pursue legal action for that research. It does not authorize testing anyone else's systems, and it does not bind third parties.
