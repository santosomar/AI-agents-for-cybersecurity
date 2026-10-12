# Shared helpers for the Part 7 tokenomics examples.
# Loads the price sheet in pricing.yaml and turns token counts into dollars.

# Instructor: Omar Santos @santosomar

from dataclasses import dataclass
from pathlib import Path

import yaml

PRICING_FILE = Path(__file__).parent / "pricing.yaml"
PER_MILLION = 1_000_000


@dataclass(frozen=True)
class ModelPrice:
    """USD per 1M tokens for one model on the Standard tier."""

    name: str
    provider: str
    input: float
    cached_input: float
    cache_write: float
    output: float
    cache_write_1h: float | None = None


def load_pricing(path: Path = PRICING_FILE) -> dict:
    """Read the raw YAML price sheet."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_models(path: Path = PRICING_FILE) -> dict[str, ModelPrice]:
    """Return {model_name: ModelPrice} for every model in the price sheet."""
    sheet = load_pricing(path)
    return {
        name: ModelPrice(name=name, **fields) for name, fields in sheet["models"].items()
    }


def tier_multiplier(tier: str = "standard", path: Path = PRICING_FILE) -> float:
    """Batch and Flex are 0.5x, Priority is ~2x. The multiplier applies to every line."""
    return load_pricing(path)["tiers"][tier]


def request_cost(
    price: ModelPrice,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0,
    cache_write_tokens: int = 0,
    cache_write_1h_tokens: int = 0,
    tier: str = "standard",
) -> float:
    """Dollar cost of one API call.

    `input_tokens` is the TOTAL prompt size, as reported by the provider. Cached and
    cache-write tokens are subsets of it, so they are removed before billing the rest
    at the ordinary input rate.
    """
    uncached = input_tokens - cached_tokens - cache_write_tokens - cache_write_1h_tokens
    if uncached < 0:
        raise ValueError("cached + cache-write tokens cannot exceed input_tokens")

    write_1h_rate = price.cache_write_1h if price.cache_write_1h is not None else price.cache_write
    dollars = (
        uncached * price.input
        + cached_tokens * price.cached_input
        + cache_write_tokens * price.cache_write
        + cache_write_1h_tokens * write_1h_rate
        + output_tokens * price.output
    ) / PER_MILLION
    return dollars * tier_multiplier(tier)


def usd(amount: float) -> str:
    """Format small dollar amounts without hiding the significant digits."""
    if amount == 0:
        return "$0"
    if abs(amount) < 0.01:
        return f"${amount:.5f}"
    if abs(amount) < 1:
        return f"${amount:.4f}"
    return f"${amount:,.2f}"
