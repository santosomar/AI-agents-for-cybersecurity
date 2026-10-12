# Context compounds on every call.
#
# Chat-completion style APIs are stateless: every call re-sends the system prompt,
# the tool schemas, the full history, and every tool result so far. This script
# simulates a 20-turn agent task and compares:
#   1. No context management (history grows forever)
#   2. Compaction (summarize old turns once the context passes a threshold)
#
# Defaults reproduce the "Tokenomics: where the money goes" chart:
#   4k-token base, 2k tokens added per turn, compact at 20k tokens.
#   No management -> 460k cumulative input tokens. Compaction -> 250k.
#
# It also reproduces the "Context compounds on every call" chart, where by the fourth
# call 76% of input tokens are context the model has already processed.
#
# Runs fully offline. Pass --plot to save a PNG chart to part7_tokenomics/output/.
#
# Instructor: Omar Santos @santosomar

import argparse
from pathlib import Path

from token_math import load_models, request_cost, usd


def simulate(
    turns: int,
    base_tokens: int,
    tokens_per_turn: int,
    compact_at: int | None,
    compact_to: int,
) -> list[int]:
    """Return the input-token size of each call.

    Each turn adds `tokens_per_turn` (user message + tool output + model reply) to the
    context. When compaction is enabled and the next call would exceed `compact_at`,
    the history is replaced by a summary so the context drops back to `compact_to`.
    """
    per_call = []
    context = base_tokens
    for turn in range(1, turns + 1):
        if turn > 1:
            context += tokens_per_turn
            if compact_at is not None and context > compact_at:
                context = compact_to
        per_call.append(context)
    return per_call


def cumulative(values: list[int]) -> list[int]:
    total, out = 0, []
    for v in values:
        total += v
        out.append(total)
    return out


def resent_share(per_call: list[int], call_index: int) -> float:
    """Share of a call's input that was already sent on the previous call."""
    if call_index == 0:
        return 0.0
    return per_call[call_index - 1] / per_call[call_index]


def print_growth_table(no_mgmt: list[int], compacted: list[int]) -> None:
    cum_a, cum_b = cumulative(no_mgmt), cumulative(compacted)
    print(f"{'Turn':>4} | {'No mgmt (call)':>14} | {'Cumulative':>10} | {'Compacted (call)':>16} | {'Cumulative':>10}")
    print("-" * 68)
    for i in range(len(no_mgmt)):
        print(
            f"{i + 1:>4} | {no_mgmt[i]:>14,} | {cum_a[i]:>10,} | {compacted[i]:>16,} | {cum_b[i]:>10,}"
        )
    saved = 1 - cum_b[-1] / cum_a[-1]
    print("-" * 68)
    print(f"Cumulative input: {cum_a[-1]:,} vs {cum_b[-1]:,} tokens ({saved:.0%} fewer with compaction)\n")


def print_resent_example() -> None:
    """The 'Context Compounds on Every Call' slide: 7k, +3k, +3k, +4k."""
    new_tokens = [7000, 3000, 3000, 4000]
    per_call = cumulative(new_tokens)
    print("Input tokens per call (re-sent context vs new tokens)")
    print(f"{'Call':>4} | {'Re-sent':>8} | {'New':>6} | {'Total':>7} | {'Re-sent %':>9}")
    print("-" * 46)
    for i, total in enumerate(per_call):
        resent = per_call[i - 1] if i else 0
        print(f"{i + 1:>4} | {resent:>8,} | {new_tokens[i]:>6,} | {total:>7,} | {resent_share(per_call, i):>9.0%}")
    print()


def print_cost(no_mgmt: list[int], compacted: list[int], output_per_turn: int) -> None:
    """Price both strategies on a few models. Output tokens are the same either way."""
    models = load_models()
    print(f"Cost of the whole task (no caching, {output_per_turn} output tokens per turn)")
    print(f"{'Model':<24} | {'No mgmt':>10} | {'Compacted':>10} | {'Saved':>10}")
    print("-" * 64)
    for name in ["gpt-6-luna", "gpt-6.1-sol", "claude-sonnet-5", "claude-opus-5", "gemini-3.8-flash"]:
        price = models[name]
        a = sum(request_cost(price, t, output_per_turn) for t in no_mgmt)
        b = sum(request_cost(price, t, output_per_turn) for t in compacted)
        print(f"{name:<24} | {usd(a):>10} | {usd(b):>10} | {usd(a - b):>10}")
    print(
        "\nNote: compaction itself costs a summarization call. On short tasks that cost can"
        "\noutweigh the savings; on long tasks the quadratic growth dominates.\n"
    )


def save_plot(no_mgmt: list[int], compacted: list[int], compact_at: int) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    turns = list(range(1, len(no_mgmt) + 1))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(turns, [t / 1000 for t in cumulative(no_mgmt)], marker="o", color="#2e7d32", label="No context management")
    ax.plot(turns, [t / 1000 for t in cumulative(compacted)], marker="o", color="#1f5f7a", label=f"Compact at {compact_at // 1000}k tokens")
    ax.set_title(f"Cumulative input tokens over a {len(turns)}-turn task (thousands)")
    ax.set_xlabel("Turn")
    ax.set_xticks(turns)
    ax.grid(axis="y", alpha=0.3)
    ax.legend()

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "context_growth.png"
    fig.savefig(out_file, dpi=150, bbox_inches="tight")
    print(f"Chart saved to {out_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate context growth in a multi-turn agent task.")
    parser.add_argument("--turns", type=int, default=20)
    parser.add_argument("--base", type=int, default=4000, help="system prompt + tool schemas")
    parser.add_argument("--per-turn", type=int, default=2000, help="tokens added to context per turn")
    parser.add_argument("--compact-at", type=int, default=20000)
    parser.add_argument("--compact-to", type=int, default=8000, help="base + summary size after compaction")
    parser.add_argument("--output-per-turn", type=int, default=500)
    parser.add_argument("--plot", action="store_true", help="save a PNG chart")
    args = parser.parse_args()

    no_mgmt = simulate(args.turns, args.base, args.per_turn, None, args.compact_to)
    compacted = simulate(args.turns, args.base, args.per_turn, args.compact_at, args.compact_to)

    print_resent_example()
    print_growth_table(no_mgmt, compacted)
    print_cost(no_mgmt, compacted, args.output_per_turn)

    if args.plot:
        save_plot(no_mgmt, compacted, args.compact_at)


if __name__ == "__main__":
    main()
