# Fewer tools: every tool schema is paid for on every request.
#
# When an agent has tools, the provider injects every tool's name, description, and
# JSON parameter schema into the prompt on EVERY call. Connect a few MCP servers and
# you can be paying for thousands of schema tokens before the model reads the alert.
#
# This script:
#   1. Counts the real token cost of a typical security toolset with tiktoken
#   2. Prunes the toolset by intent and measures the savings
#   3. Caps large tool output (an nmap scan) before it enters the context
#
# Runs offline once the tiktoken encoding is cached (first run downloads it).
#
# Instructor: Omar Santos @santosomar

import json

from token_math import load_models, request_cost, usd


def make_counter():
    try:
        import tiktoken

        enc = tiktoken.get_encoding("o200k_base")
        return lambda text: len(enc.encode(text)), "tiktoken o200k_base"
    except Exception:
        return lambda text: max(1, len(text) // 4), "approximation (4 chars per token)"


count_tokens, COUNTER_NAME = make_counter()


def tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": {"type": "object", "properties": properties, "required": required},
    }


S = {"type": "string"}
I = {"type": "integer"}

TOOLS = [
    tool("run_nmap_scan", "Run an nmap scan against an authorized target and return open ports and services.",
         {"target": {**S, "description": "IP, CIDR, or hostname in the approved scope"},
          "ports": {**S, "description": "Port list or range, e.g. 1-1024"},
          "arguments": {**S, "description": "Extra nmap flags such as -sV"}}, ["target"]),
    tool("get_cisa_kev_catalog", "Fetch the CISA Known Exploited Vulnerabilities catalog, optionally filtered.",
         {"vendor": S, "product": S, "since": {**S, "description": "ISO date"}}, []),
    tool("shodan_host_lookup", "Look up a host on Shodan and return banners, open ports, and known CVEs.",
         {"ip": S, "history": {"type": "boolean"}}, ["ip"]),
    tool("shodan_search", "Search Shodan with a query string and facets.",
         {"query": S, "facets": S, "page": I}, ["query"]),
    tool("splunk_search", "Run an SPL search over a time window and return matching events.",
         {"spl": {**S, "description": "Splunk Processing Language query"},
          "earliest": S, "latest": S, "max_results": I}, ["spl"]),
    tool("virustotal_file_report", "Get the VirusTotal report for a file hash.",
         {"sha256": S}, ["sha256"]),
    tool("virustotal_url_report", "Get the VirusTotal report for a URL.", {"url": S}, ["url"]),
    tool("whois_lookup", "Return WHOIS registration data for a domain.", {"domain": S}, ["domain"]),
    tool("dns_resolve", "Resolve DNS records for a name.",
         {"name": S, "record_type": {**S, "enum": ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]}}, ["name"]),
    tool("nvd_cve_lookup", "Fetch CVE details, CVSS vectors, and references from NVD.", {"cve_id": S}, ["cve_id"]),
    tool("edr_isolate_host", "Network-isolate a host through the EDR. Requires human approval.",
         {"hostname": S, "reason": S, "ticket_id": S}, ["hostname", "reason", "ticket_id"]),
    tool("jira_create_ticket", "Create an incident ticket.",
         {"summary": S, "description": S, "severity": {**S, "enum": ["low", "medium", "high", "critical"]},
          "assignee": S}, ["summary", "severity"]),
    tool("github_open_pr", "Open a pull request with a proposed patch.",
         {"repo": S, "branch": S, "title": S, "body": S}, ["repo", "branch", "title"]),
    tool("slack_post_message", "Post a message to a Slack channel.", {"channel": S, "text": S}, ["channel", "text"]),
]

# Which tools each kind of task actually needs. A small model or keyword rules can pick
# the intent; then only those schemas are sent.
TOOLS_BY_INTENT = {
    "enrich_ioc": {"virustotal_file_report", "virustotal_url_report", "whois_lookup", "dns_resolve", "shodan_host_lookup"},
    "vuln_triage": {"nvd_cve_lookup", "get_cisa_kev_catalog", "shodan_search"},
    "hunt": {"splunk_search"},
    "respond": {"edr_isolate_host", "jira_create_ticket", "slack_post_message"},
}


def schema_tokens(tools: list[dict]) -> int:
    return count_tokens(json.dumps(tools, separators=(",", ":")))


def section_schema_cost() -> None:
    print(f"Token counter: {COUNTER_NAME}\n")
    print("1) What each tool schema costs on every request\n")
    for t in sorted(TOOLS, key=lambda t: -schema_tokens([t])):
        print(f"   {t['name']:<24} {schema_tokens([t]):>4} tokens")
    total = schema_tokens(TOOLS)
    print(f"   {'TOTAL (' + str(len(TOOLS)) + ' tools)':<24} {total:>4} tokens\n")

    price = load_models()["gpt-6.1-sol"]
    calls_per_day = 20_000
    daily = calls_per_day * request_cost(price, total, 0)
    daily_cached = calls_per_day * request_cost(price, total, 0, cached_tokens=total)
    print(f"   At {calls_per_day:,} agent calls/day on gpt-6.1-sol the schemas alone cost"
          f" {usd(daily)}/day uncached, {usd(daily_cached)}/day if always cached.")
    print("   Real MCP servers often ship 20-50 tools with long descriptions, so multiply accordingly.\n")


def section_pruning() -> None:
    print("2) Prune tool schemas by intent\n")
    full = schema_tokens(TOOLS)
    for intent, names in TOOLS_BY_INTENT.items():
        subset = [t for t in TOOLS if t["name"] in names]
        n = schema_tokens(subset)
        print(f"   {intent:<12} {len(subset):>2} tools  {n:>4} tokens  ({1 - n / full:.0%} fewer)")
    print(
        "\n   Fewer tools also means fewer wrong tool calls and a smaller blast radius: a"
        "\n   triage step that cannot see edr_isolate_host cannot be prompt-injected into calling it.\n"
    )


def fake_nmap_output(hosts: int = 64) -> str:
    lines = ["Starting Nmap 7.95 ( https://nmap.org )"]
    for h in range(1, hosts + 1):
        lines.append(f"Nmap scan report for 10.10.0.{h}")
        lines.append("Host is up (0.0021s latency).")
        lines.append("Not shown: 995 closed tcp ports (reset)")
        lines.append("PORT     STATE SERVICE  VERSION")
        lines.append("22/tcp   open  ssh      OpenSSH 9.6p1 Ubuntu 3ubuntu13.5")
        lines.append("80/tcp   open  http     nginx 1.24.0")
        lines.append("443/tcp  open  ssl/http nginx 1.24.0")
        if h % 9 == 0:
            lines.append("3306/tcp open  mysql    MySQL 5.7.33")
        if h % 13 == 0:
            lines.append("23/tcp   open  telnet   BusyBox telnetd")
        lines.append("")
    lines.append(f"Nmap done: {hosts} IP addresses ({hosts} hosts up) scanned in 41.20 seconds")
    return "\n".join(lines)


def cap_head_tail(text: str, max_tokens: int) -> str:
    """Keep the start and end of a long output and say how much was dropped."""
    if count_tokens(text) <= max_tokens:
        return text
    lines = text.splitlines()
    head, tail = [], []
    budget = max_tokens // 2
    for line in lines:
        if count_tokens("\n".join(head + [line])) > budget:
            break
        head.append(line)
    for line in reversed(lines):
        if count_tokens("\n".join([line] + tail)) > budget:
            break
        tail.insert(0, line)
    dropped = len(lines) - len(head) - len(tail)
    return "\n".join(head + [f"... [{dropped} lines omitted; full output stored as artifact scan-001] ..."] + tail)


def summarize_nmap(text: str) -> str:
    """Deterministic, domain-aware compaction: keep only what the next step needs."""
    findings: dict[str, list[str]] = {}
    host = None
    for line in text.splitlines():
        if line.startswith("Nmap scan report for "):
            host = line.removeprefix("Nmap scan report for ")
        elif "/tcp" in line and " open " in line and host:
            port, _, service, *version = line.split()
            findings.setdefault(f"{port} {service} {' '.join(version)}".strip(), []).append(host)
    rows = [f"{svc}: {len(hosts)} hosts" + (f" ({', '.join(hosts)})" if len(hosts) <= 8 else "")
            for svc, hosts in sorted(findings.items(), key=lambda kv: len(kv[1]))]
    return "Open services (rarest first):\n" + "\n".join(rows)


def section_output_capping() -> None:
    print("3) Cap tool output before it enters the context\n")
    raw = fake_nmap_output()
    capped = cap_head_tail(raw, 600)
    summary = summarize_nmap(raw)
    print(f"   raw nmap output       {count_tokens(raw):>6} tokens")
    print(f"   head/tail cap         {count_tokens(capped):>6} tokens  (generic, loses the middle)")
    print(f"   structured summary    {count_tokens(summary):>6} tokens  (keeps every finding)\n")
    print("   " + summary.replace("\n", "\n   "))
    print(
        "\n   The summary puts rare services (telnet, old MySQL) first because those are the"
        "\n   findings. Every later call re-sends whatever you keep, so the saving repeats on"
        "\n   every turn. Store the raw output outside the context so an analyst can audit it.\n"
    )


def main() -> None:
    section_schema_cost()
    section_pruning()
    section_output_capping()


if __name__ == "__main__":
    main()
