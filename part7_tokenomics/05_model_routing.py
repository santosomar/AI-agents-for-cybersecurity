# Model routing: small model first, escalate only when needed.
#
# Two patterns:
#   Router  - decide up front which model handles a step, based on the step's intent.
#   Cascade - always try the cheap model, check the answer, escalate if the check fails.
#
# Per-token prices differ by up to 100x between tiers (gpt-6-luna input is $0.10/M,
# gpt-6-astra is $10/M), so moving the bulk of the token volume to a small model can
# cut the bill dramatically. The catch: savings only count if acceptance holds.
#
# Runs fully offline. The cascade demo uses fake model functions so you can see the
# control flow without an API key.
#
# Instructor: Omar Santos @santosomar

from collections import Counter

from pydantic import BaseModel, ValidationError, field_validator

from token_math import load_models, request_cost, usd

MODELS = load_models()

# ---------------------------------------------------------------------------
# 1) Intent-based router
# ---------------------------------------------------------------------------

# Which model tier handles which kind of SOC step. Keep this in config, not code,
# in a real deployment so you can re-route without a release.
ROUTES = {
    "extract_iocs": "gpt-6-luna",  # pull IPs, hashes, domains out of text
    "summarize_logs": "gpt-6-luna",  # compress tool output before it enters the context
    "classify_alert": "gpt-6-luna",  # benign / suspicious / malicious
    "triage_reasoning": "gpt-6.1-sol",  # correlate signals, decide next step
    "write_patch": "claude-opus-5",  # code changes that a human will merge
    "exploitability": "gpt-6-astra",  # hardest reasoning, rare
}

# One day of work for a SOC agent: (step, count, input tokens, output tokens)
DAILY_MIX = [
    ("extract_iocs", 1200, 3000, 300),
    ("summarize_logs", 900, 8000, 500),
    ("classify_alert", 1200, 2500, 50),
    ("triage_reasoning", 300, 12000, 1200),
    ("write_patch", 20, 20000, 3000),
    ("exploitability", 5, 30000, 4000),
]


def section_router() -> None:
    print("1) Intent router vs. one frontier model for everything (one day of SOC work)\n")
    frontier = MODELS["gpt-6-astra"]
    all_frontier = routed = 0.0
    volume = Counter()
    print(f"   {'Step':<18} | {'Calls':>5} | {'Model':<16} | {'Routed':>9} | {'All-frontier':>12}")
    print("   " + "-" * 72)
    for step, calls, tin, tout in DAILY_MIX:
        model = ROUTES[step]
        r = calls * request_cost(MODELS[model], tin, tout)
        f = calls * request_cost(frontier, tin, tout)
        routed += r
        all_frontier += f
        volume[model] += calls * (tin + tout)
        print(f"   {step:<18} | {calls:>5} | {model:<16} | {usd(r):>9} | {usd(f):>12}")
    print("   " + "-" * 72)
    print(f"   {'Total':<18} | {'':>5} | {'':<16} | {usd(routed):>9} | {usd(all_frontier):>12}")
    total_tokens = sum(volume.values())
    small_share = volume["gpt-6-luna"] / total_tokens
    print(f"\n   {small_share:.0%} of tokens go to the small model. Routed cost is"
          f" {routed / all_frontier:.0%} of all-frontier.\n")


# ---------------------------------------------------------------------------
# 2) Cascade economics and the escalation trap
# ---------------------------------------------------------------------------


def cascade_cost(cheap: float, strong: float, resolve_rate: float, verifier: float = 0.0) -> float:
    """Expected cost per task: cheap attempt + check on every task, strong model on escalations."""
    return cheap + verifier + (1 - resolve_rate) * strong


def section_cascade() -> None:
    cheap = request_cost(MODELS["gpt-6-luna"], 6000, 600)
    strong = request_cost(MODELS["gpt-6.1-sol"], 6000, 600)
    print("2) Cascade: gpt-6-luna first, escalate to gpt-6.1-sol when the check fails")
    print(f"   cheap attempt {usd(cheap)}, strong attempt {usd(strong)}\n")
    print(f"   {'Cheap resolves':>14} | {'Cost/task':>10} | {'vs strong-only':>14}")
    print("   " + "-" * 46)
    for rate in [0.9, 0.7, 0.5, 0.2, 0.0]:
        c = cascade_cost(cheap, strong, rate)
        note = "  <- escalation trap: paying for both" if rate == 0 else ""
        print(f"   {rate:>14.0%} | {usd(c):>10} | {c / strong:>14.0%}{note}")
    print(
        "\n   Monitor the escalation rate like an SLO. A too-strict validator or a format"
        "\n   change in the cheap model silently pushes escalations toward 100%."
        "\n   The opposite failure is worse: a too-lenient check lets wrong answers through,"
        "\n   and they come back as human review cost (see 04_cost_per_outcome.py).\n"
    )


# ---------------------------------------------------------------------------
# 3) A runnable cascade with schema validation as the check
# ---------------------------------------------------------------------------


class TriageVerdict(BaseModel):
    verdict: str
    confidence: float
    mitre_technique: str

    @field_validator("verdict")
    @classmethod
    def known_verdict(cls, v: str) -> str:
        if v not in {"benign", "suspicious", "malicious"}:
            raise ValueError(f"unknown verdict {v!r}")
        return v

    @field_validator("mitre_technique")
    @classmethod
    def looks_like_attack_id(cls, v: str) -> str:
        if not (v.startswith("T") and v[1:5].isdigit()):
            raise ValueError("expected a MITRE ATT&CK ID such as T1059")
        return v


def fake_small_model(alert: str) -> dict:
    """Stands in for gpt-6-luna. Fine on simple alerts, sloppy on complex ones."""
    if "powershell" in alert.lower():
        return {"verdict": "malicious", "confidence": 0.91, "mitre_technique": "T1059.001"}
    return {"verdict": "probably bad", "confidence": 0.4, "mitre_technique": "lateral movement"}


def fake_large_model(alert: str) -> dict:
    """Stands in for gpt-6.1-sol."""
    return {"verdict": "suspicious", "confidence": 0.82, "mitre_technique": "T1021.002"}


def triage_with_cascade(alert: str, min_confidence: float = 0.7) -> tuple[TriageVerdict, str]:
    try:
        verdict = TriageVerdict(**fake_small_model(alert))
        if verdict.confidence >= min_confidence:
            return verdict, "small"
    except ValidationError:
        pass
    return TriageVerdict(**fake_large_model(alert)), "large (escalated)"


def section_cascade_demo() -> None:
    print("3) Cascade demo with Pydantic validation as the escalation check\n")
    alerts = [
        "EDR: encoded PowerShell spawned by winword.exe on HR-LAPTOP-17",
        "Auth: admin SMB logins from 10.0.4.22 to 14 hosts in 3 minutes",
    ]
    for alert in alerts:
        verdict, used = triage_with_cascade(alert)
        print(f"   {alert}")
        print(f"     -> {verdict.verdict} ({verdict.mitre_technique}, conf {verdict.confidence}) via {used} model\n")


def main() -> None:
    section_router()
    section_cascade()
    section_cascade_demo()


if __name__ == "__main__":
    main()
