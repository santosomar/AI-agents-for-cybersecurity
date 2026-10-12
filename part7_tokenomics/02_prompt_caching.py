# Prompt caching: reuse the stable prefix at a fraction of the input price.
#
# Scenario: a SOC alert-triage agent. Every call sends the same stable prefix
# (system prompt + tool schemas + triage runbook), then one new alert.
#
#   [ system prompt | tool schemas | runbook ]  [ alert #N ]
#   <------------- stable prefix ------------>  <- varies ->
#
# Providers cache the prefix and bill re-use at a discount (October 2026):
#   - OpenAI GPT-5.6+: write 1.25x input, read 0.1x (0.05x on GPT-6.1 Sol), TTL >= 30 min
#   - Anthropic: write 1.25x (5-minute TTL) or 2x (1-hour TTL), read 0.1x (lower on some models)
#   - Google Gemini: implicit caching, write at 1x, read 0.1x
#
# This script shows:
#   1. Cost with and without caching for a day of alerts
#   2. Why the TTL must match how often requests arrive (5-minute vs 1-hour)
#   3. The ordering mistake: a timestamp at the top of the prompt destroys the cache
#
# Runs fully offline.
#
# Instructor: Omar Santos @santosomar

import argparse

from token_math import ModelPrice, load_models, request_cost, usd


def simulate_day(
    price: ModelPrice,
    alerts: int,
    gap_minutes: float,
    prefix_tokens: int,
    variable_tokens: int,
    output_tokens: int,
    ttl_minutes: float | None,
    write_field: str = "cache_write",
) -> tuple[float, int, int]:
    """Return (total_cost, cache_writes, cache_hits) for one day of alerts.

    A request is a cache hit when the previous request arrived within the TTL.
    Hits refresh the TTL. `ttl_minutes=None` means caching is off.
    """
    total, writes, hits = 0.0, 0, 0
    for i in range(alerts):
        input_tokens = prefix_tokens + variable_tokens
        if ttl_minutes is None:
            total += request_cost(price, input_tokens, output_tokens)
            continue

        is_hit = i > 0 and gap_minutes <= ttl_minutes
        if is_hit:
            hits += 1
            total += request_cost(price, input_tokens, output_tokens, cached_tokens=prefix_tokens)
        else:
            writes += 1
            kwargs = {"cache_write_1h_tokens" if write_field == "cache_write_1h" else "cache_write_tokens": prefix_tokens}
            total += request_cost(price, input_tokens, output_tokens, **kwargs)
    return total, writes, hits


def section_daily_savings(models: dict[str, ModelPrice], args: argparse.Namespace) -> None:
    print(f"1) One day of triage: {args.alerts} alerts, one every {args.gap} min")
    print(f"   prefix={args.prefix:,} tokens, alert={args.variable:,} tokens, output={args.output:,} tokens\n")
    print(f"{'Model':<20} | {'No cache':>10} | {'Cached':>10} | {'Saved':>6} | {'Writes':>6} | {'Hits':>5}")
    print("-" * 72)
    # OpenAI keeps caches for at least 30 minutes; Anthropic default is 5 minutes;
    # Gemini implicit caches typically live minutes to hours (we assume 30 here).
    ttl_by_provider = {"openai": 30, "anthropic": 5, "google": 30}
    for name in ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-sol", "claude-haiku-4.5", "claude-sonnet-5", "claude-opus-5", "gemini-3.8-flash"]:
        price = models[name]
        base, _, _ = simulate_day(price, args.alerts, args.gap, args.prefix, args.variable, args.output, None)
        cached, writes, hits = simulate_day(
            price, args.alerts, args.gap, args.prefix, args.variable, args.output, ttl_by_provider[price.provider]
        )
        print(f"{name:<20} | {usd(base):>10} | {usd(cached):>10} | {1 - cached / base:>6.0%} | {writes:>6} | {hits:>5}")
    print()


def section_ttl(models: dict[str, ModelPrice], args: argparse.Namespace) -> None:
    price = models["claude-sonnet-5"]
    print("2) Match the TTL to the traffic pattern (claude-sonnet-5, 40 alerts)")
    print(f"{'Gap between alerts':>20} | {'No cache':>10} | {'5-min TTL':>10} | {'1-hour TTL':>10}")
    print("-" * 60)
    for gap in [1, 4, 10, 30, 90]:
        none, _, _ = simulate_day(price, 40, gap, args.prefix, args.variable, args.output, None)
        five, _, _ = simulate_day(price, 40, gap, args.prefix, args.variable, args.output, 5)
        hour, _, _ = simulate_day(price, 40, gap, args.prefix, args.variable, args.output, 60, "cache_write_1h")
        print(f"{str(gap) + ' min':>20} | {usd(none):>10} | {usd(five):>10} | {usd(hour):>10}")
    print(
        "\n   Under 5 minutes: the cheaper 5-minute write wins."
        "\n   5 to 60 minutes: the 5-minute cache expires every time, so you pay the 1.25x"
        "\n   write on every call and never collect a read. The 1-hour TTL wins."
        "\n   Over 60 minutes: neither cache survives. Caching costs MORE than no caching.\n"
    )


def section_break_even() -> None:
    print("3) Break-even math (multiples of the prefix's normal input cost)")
    print(f"{'Calls':>5} | {'No cache':>8} | {'5m write + reads':>16} | {'1h write + reads':>16}")
    print("-" * 56)
    for calls in [1, 2, 3, 5, 10]:
        reads = calls - 1
        print(f"{calls:>5} | {calls:>7.2f}x | {1.25 + 0.1 * reads:>15.2f}x | {2.0 + 0.1 * reads:>15.2f}x")
    print("   A 1.25x write pays for itself on the first read. A 2x write needs two reads.\n")


def section_ordering(models: dict[str, ModelPrice], args: argparse.Namespace) -> None:
    price = models["gpt-6.1-sol"]
    print("4) The ordering mistake (gpt-6.1-sol)")
    good, _, _ = simulate_day(price, args.alerts, args.gap, args.prefix, args.variable, args.output, 30)
    # A timestamp or alert ID at the top of the prompt changes the first tokens on every
    # call, so nothing after it can ever match. Every call becomes a fresh cache write.
    bad = sum(
        request_cost(price, args.prefix + args.variable, args.output, cache_write_tokens=args.prefix)
        for _ in range(args.alerts)
    )
    none, _, _ = simulate_day(price, args.alerts, args.gap, args.prefix, args.variable, args.output, None)
    print(f"   Stable content first, alert last : {usd(good)}")
    print(f"   No caching at all                : {usd(none)}")
    print(f"   Timestamp first (all writes)     : {usd(bad)}  <- worse than no caching")
    print(
        "\n   Rules: static content first, variable content last. Keep tool definitions in a"
        "\n   fixed order. Do not inject dates, request IDs, or user names into the system prompt.\n"
    )


def section_security() -> None:
    print("5) Security notes for cached prompts")
    print(
        "   - Never put secrets or per-customer data in a shared prefix. Caches are keyed on"
        "\n     content, and timing differences between hits and misses can leak whether a"
        "\n     prefix was seen before."
        "\n   - Use a per-tenant prompt_cache_key (OpenAI) so cache accounting and reuse stay"
        "\n     inside one customer or workspace."
        "\n   - Track cache-hit rate (cached_tokens / input_tokens) as an operational metric."
        "\n     A sudden drop usually means someone changed the system prompt or tool order.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Prompt caching cost calculator for a triage agent.")
    parser.add_argument("--alerts", type=int, default=200)
    parser.add_argument("--gap", type=float, default=3, help="minutes between alerts")
    parser.add_argument("--prefix", type=int, default=12000, help="stable prefix tokens")
    parser.add_argument("--variable", type=int, default=1000, help="per-alert tokens")
    parser.add_argument("--output", type=int, default=400, help="output tokens per alert")
    args = parser.parse_args()

    models = load_models()
    section_daily_savings(models, args)
    section_ttl(models, args)
    section_break_even()
    section_ordering(models, args)
    section_security()


if __name__ == "__main__":
    main()
