# Batch: run offline work at roughly half price.
#
# OpenAI, Anthropic, and Google all bill Batch API requests at 50% of the standard
# rate in exchange for asynchronous processing (results within 24 hours). Cache
# discounts stack on top of the batch discount.
#
# Good batch work in a security program: re-scoring yesterday's closed alerts,
# enriching a backlog of scanner findings, tagging CVEs with ATT&CK techniques,
# running regression evals on a new prompt. Bad batch work: anything a person or
# an agent loop is waiting on.
#
# This script writes an OpenAI Batch JSONL file for a backlog of findings, compares
# standard vs batch cost, and optionally submits the job.
#
#   python 08_batch_triage.py              build file + estimate cost (offline)
#   python 08_batch_triage.py --submit     also upload and create the batch (needs OPENAI_API_KEY)
#
# Instructor: Omar Santos @santosomar

import argparse
import json
import random
from pathlib import Path

from token_math import load_models, request_cost, usd

OUTPUT_DIR = Path(__file__).parent / "output"

SYSTEM_PROMPT = (
    "You are a vulnerability management analyst. For each scanner finding, return JSON "
    'with keys "priority" (P1-P4), "reason" (one sentence), and "kev_likely" (true/false).'
)

FINDING_TEMPLATES = [
    "Host {host}: Apache Tomcat 9.0.{n} detected, manager interface reachable from the internet.",
    "Host {host}: OpenSSH 8.{n} with password authentication enabled.",
    "Host {host}: TLS 1.0 and TLS 1.1 enabled on port 443.",
    "Host {host}: Microsoft Exchange build 15.2.{n} missing latest security update.",
    "Host {host}: Jenkins 2.{n} script console accessible without authentication.",
]


def synthetic_findings(count: int, seed: int = 7) -> list[str]:
    """Synthetic data only. Never put real hostnames, credentials, or customer data in examples."""
    rng = random.Random(seed)
    return [
        rng.choice(FINDING_TEMPLATES).format(host=f"10.20.{rng.randint(0, 255)}.{rng.randint(1, 254)}", n=rng.randint(1, 99))
        for _ in range(count)
    ]


def build_batch_file(findings: list[str], model: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "batch_input.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for i, finding in enumerate(findings):
            request = {
                "custom_id": f"finding-{i:05d}",
                "method": "POST",
                "url": "/v1/responses",
                "body": {
                    "model": model,
                    # Same instructions on every line, so the prefix can be cached within the batch.
                    "instructions": SYSTEM_PROMPT,
                    "input": finding,
                    "max_output_tokens": 120,
                },
            }
            f.write(json.dumps(request) + "\n")
    return path


def estimate(findings: int, model: str, prefix_tokens: int, finding_tokens: int, output_tokens: int) -> None:
    price = load_models()[model]
    tin = prefix_tokens + finding_tokens
    standard = findings * request_cost(price, tin, output_tokens)
    batch = findings * request_cost(price, tin, output_tokens, tier="batch")
    batch_cached = request_cost(price, tin, output_tokens, cache_write_tokens=prefix_tokens, tier="batch") + (
        (findings - 1) * request_cost(price, tin, output_tokens, cached_tokens=prefix_tokens, tier="batch")
    )
    print(f"Cost estimate for {findings:,} findings on {model}")
    print(f"  ({prefix_tokens:,} prefix + {finding_tokens} finding tokens in, {output_tokens} out)\n")
    print(f"  Standard, synchronous      {usd(standard):>10}")
    print(f"  Batch (0.5x)               {usd(batch):>10}")
    print(f"  Batch + cached prefix      {usd(batch_cached):>10}  (best case: every line hits the cache)\n")


def submit(path: Path) -> None:
    import os

    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Add it to your environment or a .env file.")
    client = OpenAI()
    with open(path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="batch")
    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={"job": "nightly-finding-triage"},
    )
    print(f"Submitted batch {batch.id} (status: {batch.status}).")
    print(f"Check later with: client.batches.retrieve('{batch.id}')")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and price an OpenAI Batch triage job.")
    parser.add_argument("--findings", type=int, default=5000)
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--prefix-tokens", type=int, default=2500, help="instructions + runbook in a real job")
    parser.add_argument("--finding-tokens", type=int, default=60)
    parser.add_argument("--output-tokens", type=int, default=80)
    parser.add_argument("--submit", action="store_true")
    args = parser.parse_args()

    findings = synthetic_findings(args.findings)
    path = build_batch_file(findings, args.model)
    print(f"Wrote {len(findings):,} requests to {path}\n")
    print("First line:\n  " + path.read_text(encoding="utf-8").splitlines()[0] + "\n")

    estimate(args.findings, args.model, args.prefix_tokens, args.finding_tokens, args.output_tokens)
    print(
        "Batch files are plain text on disk and in provider storage. Redact secrets and"
        "\npersonal data before writing them, and delete input/output files when the job is done.\n"
    )
    if args.submit:
        submit(path)


if __name__ == "__main__":
    main()
