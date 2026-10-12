# Live prompt-caching check against the OpenAI Responses API.
#
# Sends several triage questions that share one long, stable prefix (an SSRF runbook
# built from part4_rag_examples/data) and prints what the API actually billed:
#   usage.input_tokens                              total prompt tokens
#   usage.input_tokens_details.cached_tokens        served from cache (cache read)
#   usage.input_tokens_details.cache_write_tokens   written to cache (GPT-5.6+)
#
# Caching only applies to prefixes of at least 1,024 tokens. The first call usually
# writes the cache; later calls with the same prefix should report cached tokens.
#
# Requires OPENAI_API_KEY (loaded from .env if present).
#
# Instructor: Omar Santos @santosomar

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from token_math import load_models, request_cost, usd

DATA_DIR = Path(__file__).parent.parent / "part4_rag_examples" / "data"

QUESTIONS = [
    "Alert: outbound request from web-01 to http://169.254.169.254/latest/meta-data/. Severity and next step?",
    "Alert: user-supplied URL parameter fetched http://localhost:8080/admin. Is this SSRF? One-line verdict.",
    "Alert: image proxy requested file:///etc/passwd. Classify and recommend a control.",
]


def build_stable_prefix() -> str:
    """Static instructions + reference material. Nothing in here changes between calls."""
    runbook = (DATA_DIR / "ssrf.txt").read_text(encoding="utf-8")
    cheatsheet = (DATA_DIR / "llm_cheatsheet.md").read_text(encoding="utf-8")
    return (
        "You are a SOC triage assistant. Answer in at most three sentences. "
        "Use only the reference material below.\n\n"
        f"## SSRF reference\n{runbook}\n\n## LLM security cheat sheet\n{cheatsheet}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Observe real cache hits on the OpenAI API.")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--tenant", default="course-demo", help="used as prompt_cache_key")
    args = parser.parse_args()

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Add it to your environment or a .env file.")

    client = OpenAI()
    prices = load_models()
    price = prices.get(args.model)
    instructions = build_stable_prefix()

    total_input = total_cached = 0
    total_cost = 0.0
    print(f"Model: {args.model}\n")
    print(f"{'Call':>4} | {'Input':>6} | {'Cached':>6} | {'Written':>7} | {'Output':>6} | {'Cost':>9}")
    print("-" * 56)
    for i, question in enumerate(QUESTIONS, start=1):
        # `instructions` is the stable prefix; the alert goes last so the prefix can match.
        response = client.responses.create(
            model=args.model,
            instructions=instructions,
            input=question,
            prompt_cache_key=args.tenant,
        )
        usage = response.usage
        details = usage.input_tokens_details
        cached = getattr(details, "cached_tokens", 0) or 0
        written = getattr(details, "cache_write_tokens", 0) or 0

        cost = (
            request_cost(price, usage.input_tokens, usage.output_tokens, cached_tokens=cached, cache_write_tokens=written)
            if price
            else 0.0
        )
        total_input += usage.input_tokens
        total_cached += cached
        total_cost += cost
        print(f"{i:>4} | {usage.input_tokens:>6} | {cached:>6} | {written:>7} | {usage.output_tokens:>6} | {usd(cost):>9}")

    hit_rate = total_cached / total_input if total_input else 0
    print("-" * 56)
    print(f"Token cache-hit rate: {hit_rate:.0%}   Estimated cost: {usd(total_cost)}")
    if price is None:
        print(f"(No price for {args.model} in pricing.yaml, so cost shows $0.)")


if __name__ == "__main__":
    main()
