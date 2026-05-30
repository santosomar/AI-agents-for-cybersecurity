# DeepAgents Example: Autonomous SOC (Security Operations Center) Agent
#
# This script builds a SOC analyst agent using the `deepagents` library. A single
# "SOC supervisor" deep agent coordinates five specialized subagents that mirror
# the real workflow of a Tier-1/Tier-2 analyst:
#
#   1. Triage        - filter and prioritize the incoming alert queue
#   2. Enrichment    - pull context (asset owner, user history, threat-intel reputation)
#   3. Investigation - form hypotheses, query logs, reconstruct the timeline
#   4. Correlation   - link signals across tools into one coherent incident story
#   5. Response      - recommend / stage containment (isolate, disable, block) with approval
#
# Why deepagents? The library gives us, for free:
#   - write_todos       -> the supervisor plans the investigation before acting
#   - a virtual filesystem (write_file/read_file) -> offload large log/alert blobs
#   - the `task` tool    -> delegate to subagents so each one works in a CLEAN context
#                           (the supervisor only sees concise summaries, not raw logs)
#
# Everything runs against an in-memory, SIMULATED SOC environment (alerts, assets,
# users, threat intel, logs). No real SIEM, EDR, or network is touched, so the
# example is completely safe to run. Only the LLM calls require network + an API key.
#
# Instructor: Omar Santos @santosomar
#
# Run it self-contained with uv (no project sync needed):
#   uv run part5_agents_and_tools/deepagents_example/soc_agent.py
# The PEP 723 metadata block below lets uv build an isolated environment with
# only this script's dependencies.

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "deepagents",
#     "langchain-openai",
#     "python-dotenv",
# ]
# ///

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from deepagents import create_deep_agent

# Load OPENAI_API_KEY (and friends) from a .env file if present.
load_dotenv()

# Quiet LangSmith tracing unless it is explicitly configured with an API key.
# Without a valid key/plan, every run upload returns HTTP 403 and floods the
# console with "Failed to multipart ingest runs" noise. If you DO have a
# LangSmith key set, tracing is left enabled so you can observe the run.
if not (os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")):
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

# The provider:model string deepagents will use for the supervisor and, by
# default, every subagent. Keep it consistent with the rest of the repo.
MODEL = "openai:gpt-5.4-mini"


# ======================================================================
# 1. SIMULATED SOC ENVIRONMENT
# ----------------------------------------------------------------------
# A small, self-consistent dataset describing one realistic incident:
# a phishing-driven credential theft on a finance workstation that escalates
# into lateral movement and command-and-control (C2) traffic. The noise alerts
# exist so the triage subagent has something to correctly suppress.
# ======================================================================

ALERT_QUEUE = [
    {
        "alert_id": "ALRT-1001",
        "severity": "high",
        "title": "Suspicious PowerShell with encoded command",
        "host": "WKS-4471",
        "user": "jdoe",
        "source": "EDR",
        "indicators": {"process": "powershell.exe", "parent": "outlook.exe"},
    },
    {
        "alert_id": "ALRT-1002",
        "severity": "high",
        "title": "Impossible travel sign-in",
        "host": None,
        "user": "jdoe",
        "source": "Identity Provider",
        "indicators": {"ip": "185.220.101.47", "country": "RO"},
    },
    {
        "alert_id": "ALRT-1003",
        "severity": "critical",
        "title": "Outbound connection to known C2 server",
        "host": "WKS-4471",
        "user": "jdoe",
        "source": "Firewall",
        "indicators": {"ip": "185.220.101.47", "port": 443},
    },
    {
        "alert_id": "ALRT-1004",
        "severity": "low",
        "title": "Windows Defender definitions updated",
        "host": "WKS-2210",
        "user": "system",
        "source": "EDR",
        "indicators": {},
    },
    {
        "alert_id": "ALRT-1005",
        "severity": "informational",
        "title": "Scheduled vulnerability scan completed",
        "host": "SCANNER-01",
        "user": "svc_scanner",
        "source": "Vuln Scanner",
        "indicators": {},
    },
]

ASSET_INVENTORY = {
    "WKS-4471": {
        "owner": "jdoe",
        "department": "Finance",
        "criticality": "high",
        "os": "Windows 11",
        "data_classification": "confidential (financial records)",
    },
    "WKS-2210": {
        "owner": "asmith",
        "department": "Marketing",
        "criticality": "low",
        "os": "Windows 11",
        "data_classification": "internal",
    },
}

USER_DIRECTORY = {
    "jdoe": {
        "full_name": "Jane Doe",
        "title": "Senior Financial Analyst",
        "privileges": "local admin on WKS-4471; access to finance file shares",
        "mfa_enabled": True,
        "recent_events": "Password unchanged 240 days; clicked link in an email 35 min ago",
    },
}

# Threat-intel reputation. Hash is a SHA-256 placeholder (no weak algorithms).
THREAT_INTEL = {
    "185.220.101.47": {
        "verdict": "malicious",
        "categories": ["c2", "tor-exit-node"],
        "confidence": 95,
        "last_seen": "active in the last 24h",
    },
    "a3f1c9d2e4b5076889aabbccddeeff00112233445566778899aabbccddeeff00": {
        "verdict": "malicious",
        "categories": ["trojan", "loader"],
        "confidence": 88,
        "last_seen": "2 days ago",
    },
}

# Simulated SIEM/EDR log lines, keyed loosely by topic so a substring query
# can return relevant entries.
SIEM_LOGS = [
    "2026-05-30T13:58:02Z host=WKS-4471 user=jdoe outlook.exe opened attachment 'Invoice_May.docm'",
    "2026-05-30T13:58:40Z host=WKS-4471 user=jdoe powershell.exe -enc <base64> spawned by outlook.exe",
    "2026-05-30T13:58:55Z host=WKS-4471 powershell.exe downloaded http://185.220.101.47/payload.bin",
    "2026-05-30T13:59:10Z host=WKS-4471 new file C:\\Users\\jdoe\\AppData\\update.exe sha256=a3f1c9d2e4b50768...",
    "2026-05-30T14:01:33Z host=WKS-4471 outbound TLS to 185.220.101.47:443 bytes_out=48211",
    "2026-05-30T14:03:12Z host=WKS-4471 user=jdoe SMB session to WKS-2210 (admin$)",
    "2026-05-30T14:05:48Z idp user=jdoe sign-in from 185.220.101.47 (RO) success - impossible travel vs 14:00 US sign-in",
]


# ======================================================================
# 2. TOOLS (grouped by SOC phase)
# ----------------------------------------------------------------------
# Plain Python functions become tools. Each has a clear docstring because the
# LLM reads it to decide when and how to call the tool. Returning JSON strings
# keeps tool output structured and easy for the model to parse.
# ======================================================================

# --- Triage tools ---------------------------------------------------------

def get_alert_queue() -> str:
    """Return the current queue of open security alerts.

    Each alert includes its id, severity, title, affected host/user, source
    product, and any indicators of compromise (IPs, hashes, process names).
    Use this first to see everything that needs triage.
    """
    summary = [
        {
            "alert_id": a["alert_id"],
            "severity": a["severity"],
            "title": a["title"],
            "host": a["host"],
            "user": a["user"],
        }
        for a in ALERT_QUEUE
    ]
    return json.dumps(summary, indent=2)


def get_alert_details(alert_id: str) -> str:
    """Return the full details (including indicators) for a single alert id."""
    for alert in ALERT_QUEUE:
        if alert["alert_id"] == alert_id:
            return json.dumps(alert, indent=2)
    return json.dumps({"error": f"No alert found with id {alert_id}"})


# --- Enrichment tools -----------------------------------------------------

def lookup_asset(hostname: str) -> str:
    """Look up an asset in the CMDB: owner, department, criticality, and the
    data classification stored on the host. Use this to judge business impact.
    """
    asset = ASSET_INVENTORY.get(hostname)
    if asset is None:
        return json.dumps({"hostname": hostname, "note": "Asset not found in inventory"})
    return json.dumps({"hostname": hostname, **asset}, indent=2)


def lookup_user(username: str) -> str:
    """Look up a user in the directory: role, privileges, MFA status, and recent
    notable account events. Use this to understand blast radius and account risk.
    """
    user = USER_DIRECTORY.get(username)
    if user is None:
        return json.dumps({"username": username, "note": "User not found in directory"})
    return json.dumps({"username": username, **user}, indent=2)


def check_threat_intel(indicator: str) -> str:
    """Check an indicator (IP address, domain, or SHA-256 file hash) against the
    threat-intelligence platform. Returns a verdict, categories, and a
    confidence score. Use this to decide whether an indicator is malicious.
    """
    intel = THREAT_INTEL.get(indicator)
    if intel is None:
        return json.dumps(
            {"indicator": indicator, "verdict": "unknown", "note": "No matching intel"}
        )
    return json.dumps({"indicator": indicator, **intel}, indent=2)


# --- Investigation tools --------------------------------------------------

def query_siem_logs(search: str, max_results: int = 10) -> str:
    """Search the SIEM/EDR logs for lines containing the given substring
    (e.g. a hostname, username, IP, or process name). Returns matching log
    lines in chronological order. Use this to reconstruct what happened.
    """
    needle = search.lower()
    matches = [line for line in SIEM_LOGS if needle in line.lower()]
    return json.dumps(matches[:max_results], indent=2)


def get_process_tree(hostname: str) -> str:
    """Return the suspicious process ancestry observed on a host. Use this to
    confirm how a process was launched (e.g. email client -> script interpreter).
    """
    if hostname == "WKS-4471":
        tree = "outlook.exe -> powershell.exe (-enc) -> update.exe -> cmd.exe (smb to WKS-2210)"
        return json.dumps({"hostname": hostname, "process_tree": tree})
    return json.dumps({"hostname": hostname, "process_tree": "no suspicious ancestry observed"})


# --- Correlation tools ----------------------------------------------------

def find_related_alerts(indicator: str) -> str:
    """Find every open alert that references the given indicator (IP, host, or
    user). Use this to link separate alerts into a single incident.
    """
    related = []
    for alert in ALERT_QUEUE:
        blob = json.dumps(alert).lower()
        if indicator.lower() in blob:
            related.append({"alert_id": alert["alert_id"], "title": alert["title"]})
    return json.dumps({"indicator": indicator, "related_alerts": related}, indent=2)


# --- Response tools (containment) ----------------------------------------
# These are STAGED, not executed: every action requires explicit human approval
# (the SOC's change-control / rules-of-engagement). They return a "pending
# approval" ticket. See the README for how to wire real human-in-the-loop with
# interrupt_on + a checkpointer.

def isolate_host(hostname: str, justification: str) -> str:
    """Stage network isolation of a host (EDR containment). Requires a written
    justification. Returns a pending-approval action; it does NOT execute.
    """
    return json.dumps(
        {
            "action": "isolate_host",
            "target": hostname,
            "justification": justification,
            "status": "PENDING_ANALYST_APPROVAL",
        }
    )


def disable_account(username: str, justification: str) -> str:
    """Stage a disable of a user account in the identity provider. Requires a
    written justification. Returns a pending-approval action; does NOT execute.
    """
    return json.dumps(
        {
            "action": "disable_account",
            "target": username,
            "justification": justification,
            "status": "PENDING_ANALYST_APPROVAL",
        }
    )


def block_indicator(indicator: str, justification: str) -> str:
    """Stage a firewall/EDR block of a malicious indicator (IP, domain, or hash).
    Requires a written justification. Returns a pending-approval action.
    """
    return json.dumps(
        {
            "action": "block_indicator",
            "target": indicator,
            "justification": justification,
            "status": "PENDING_ANALYST_APPROVAL",
        }
    )


# ======================================================================
# 3. SPECIALIZED SUBAGENTS
# ----------------------------------------------------------------------
# Each subagent owns ONE phase, gets only the tools it needs (least privilege +
# focus), and is told to return a concise summary so the supervisor's context
# stays clean. The supervisor calls them via the built-in `task` tool.
# ======================================================================

triage_subagent = {
    "name": "triage-analyst",
    "description": (
        "Filters and prioritizes the incoming alert queue. Use FIRST to decide "
        "which alerts are real and high priority and which are benign noise to suppress."
    ),
    "system_prompt": (
        "You are a SOC triage analyst. Pull the full alert queue, then for each "
        "alert classify it as ESCALATE (likely true positive worth investigating) "
        "or SUPPRESS (benign / informational noise) with a one-line reason and a "
        "priority (P1-P4). Suppress routine maintenance and scanner activity. "
        "Return a short ranked list of the alerts to escalate. Do NOT investigate "
        "deeply here. Keep your response under 200 words."
    ),
    "tools": [get_alert_queue, get_alert_details],
}

enrichment_subagent = {
    "name": "enrichment-analyst",
    "description": (
        "Pulls context for escalated alerts: asset owner/criticality, user "
        "privileges and history, and threat-intel reputation of indicators. Use "
        "after triage to add business and threat context."
    ),
    "system_prompt": (
        "You are a SOC enrichment analyst. For the hosts, users, and indicators "
        "you are given, look up the asset (criticality, data classification), the "
        "user (privileges, MFA, recent events), and run every IP/domain/hash "
        "through threat intel. Summarize what is malicious, what is high-value, "
        "and what raises blast-radius concerns. Keep your response under 250 words."
    ),
    "tools": [lookup_asset, lookup_user, check_threat_intel],
}

investigation_subagent = {
    "name": "investigator",
    "description": (
        "Forms and tests hypotheses by querying logs and reconstructing the "
        "process/timeline of an incident. Use to answer 'what actually happened?'."
    ),
    "system_prompt": (
        "You are a SOC investigator. State a working hypothesis, then query the "
        "SIEM logs (by host, user, and IP) and the process tree to confirm or "
        "refute it. Reconstruct a chronological timeline of attacker actions "
        "(initial access -> execution -> C2 -> lateral movement). Map key steps "
        "to MITRE ATT&CK tactics where obvious. Return the timeline and your "
        "confirmed findings. Keep your response under 300 words."
    ),
    "tools": [query_siem_logs, get_process_tree],
}

correlation_subagent = {
    "name": "correlation-analyst",
    "description": (
        "Links signals across tools into one coherent incident instead of "
        "disconnected alerts. Use to merge related alerts and tell the single story."
    ),
    "system_prompt": (
        "You are a SOC correlation analyst. Given indicators (IPs, hosts, users), "
        "find all related alerts and explain how they connect into ONE incident. "
        "Produce a single incident narrative: which alerts belong together, the "
        "shared indicators that link them, and the overall attack chain. State a "
        "severity for the unified incident. Keep your response under 250 words."
    ),
    "tools": [find_related_alerts, get_alert_details, query_siem_logs],
}

response_subagent = {
    "name": "responder",
    "description": (
        "Recommends and STAGES containment actions (isolate host, disable account, "
        "block indicator) for analyst approval. Use last, only after the incident "
        "is understood."
    ),
    "system_prompt": (
        "You are a SOC incident responder. Based on the confirmed incident, "
        "recommend proportionate containment and stage the actions using your "
        "tools, always providing a clear justification for each. Remember every "
        "action is STAGED and requires human approval before it executes - never "
        "claim an action is complete. Order actions by urgency (stop active C2 and "
        "lateral movement first). Return the list of staged actions with "
        "justifications and any follow-up recommendations. Keep it under 250 words."
    ),
    "tools": [isolate_host, disable_account, block_indicator],
}

SUBAGENTS = [
    triage_subagent,
    enrichment_subagent,
    investigation_subagent,
    correlation_subagent,
    response_subagent,
]


# ======================================================================
# 4. THE SOC SUPERVISOR (main deep agent)
# ----------------------------------------------------------------------
# The supervisor does NOT touch raw tools itself; it plans with write_todos and
# delegates each phase to the right subagent, then compiles the final report.
# ======================================================================

SOC_SUPERVISOR_PROMPT = """You are the supervisor of an autonomous Security Operations Center (SOC).

Your job is to run a full alert-to-incident workflow by delegating to your \
specialist subagents. Work through these five phases IN ORDER, using the \
`task` tool to delegate each one:

1. TRIAGE        -> task(triage-analyst): decide which alerts to escalate vs suppress.
2. ENRICHMENT    -> task(enrichment-analyst): add asset, user, and threat-intel context
                    for the escalated alerts.
3. INVESTIGATION -> task(investigator): reconstruct what happened from logs + process tree.
4. CORRELATION   -> task(correlation-analyst): link the related alerts into ONE incident.
5. RESPONSE      -> task(responder): stage containment actions for human approval.

Guidelines:
- ALWAYS start by writing a todo plan with write_todos, then update it as phases complete.
- Pass each subagent the specific context it needs (alert ids, hosts, users, indicators)
  that earlier phases surfaced.
- Delegate the heavy lifting to subagents to keep your own context clean; you synthesize.
- Containment is always STAGED and requires human approval - never state that a
  host was actually isolated or an account actually disabled.

When all five phases are done, write the final incident report to the virtual file
`incident_report.md` using write_file, then present it in your final message. The
report must contain these sections:
  - Incident Summary (2-3 sentences)
  - Severity & Priority
  - Affected Assets & Users
  - Timeline of Events
  - Indicators of Compromise (IOCs)
  - Correlated Alerts
  - Recommended / Staged Response Actions (each marked PENDING APPROVAL)
  - Analyst Next Steps
"""

agent = create_deep_agent(
    model=MODEL,
    system_prompt=SOC_SUPERVISOR_PROMPT,
    subagents=SUBAGENTS,
    name="soc-supervisor",
)


# ======================================================================
# 5. RUN THE AGENT
# ======================================================================

if __name__ == "__main__":
    user_request = (
        "Several alerts just fired. Run the full SOC workflow: triage the queue, "
        "enrich and investigate the real ones, correlate them into a single "
        "incident, and stage an appropriate response. Then give me the incident report."
    )

    print("=" * 70)
    print("  AUTONOMOUS SOC AGENT (deepagents)")
    print("=" * 70)
    print(f"\nAnalyst request:\n  {user_request}\n")
    print("Running... (the supervisor will plan, delegate to 5 subagents, and report)\n")

    result = agent.invoke({"messages": [{"role": "user", "content": user_request}]})

    print("=" * 70)
    print("  FINAL RESPONSE")
    print("=" * 70 + "\n")
    print(result["messages"][-1].content)

    # The supervisor is instructed to save the report to the virtual filesystem.
    files = result.get("files", {})
    if "incident_report.md" in files:
        print("\n" + "=" * 70)
        print("  incident_report.md (from the agent's virtual filesystem)")
        print("=" * 70 + "\n")
        print(files["incident_report.md"])
