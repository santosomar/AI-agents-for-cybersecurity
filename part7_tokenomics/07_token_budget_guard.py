# Budgets: set a token and cost ceiling per task.
#
# Agents loop. A stuck agent re-calls the same tool, re-reads the same context, and
# keeps paying for it. OWASP lists this as LLM10:2025 Unbounded Consumption; an
# attacker who can make your agent loop (for example with a prompt-injected web page)
# turns that into "denial of wallet".
#
# TokenBudget enforces three ceilings per task and also stops repeated identical tool
# calls. Run it two ways:
#   python 07_token_budget_guard.py          simulated runaway agent, no API key
#   python 07_token_budget_guard.py --live   real LangChain agent on gpt-6-luna,
#                                            budget enforced from a callback
#
# Instructor: Omar Santos @santosomar

import argparse
from dataclasses import dataclass, field

from token_math import load_models, request_cost, usd


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class TokenBudget:
    model: str
    max_input_tokens: int = 150_000
    max_output_tokens: int = 20_000
    max_usd: float = 0.50
    max_repeat_tool_calls: int = 2

    input_tokens: int = 0
    output_tokens: int = 0
    spent_usd: float = 0.0
    calls: int = 0
    _tool_calls: dict = field(default_factory=dict)

    def record_llm_call(self, input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> None:
        price = load_models()[self.model]
        self.calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.spent_usd += request_cost(price, input_tokens, output_tokens, cached_tokens=cached_tokens)
        self._check()

    def record_tool_call(self, name: str, args: str) -> None:
        key = (name, args)
        self._tool_calls[key] = self._tool_calls.get(key, 0) + 1
        if self._tool_calls[key] > self.max_repeat_tool_calls:
            raise BudgetExceeded(f"loop detected: {name}({args}) called {self._tool_calls[key]} times")

    def _check(self) -> None:
        if self.input_tokens > self.max_input_tokens:
            raise BudgetExceeded(f"input tokens {self.input_tokens:,} > {self.max_input_tokens:,}")
        if self.output_tokens > self.max_output_tokens:
            raise BudgetExceeded(f"output tokens {self.output_tokens:,} > {self.max_output_tokens:,}")
        if self.spent_usd > self.max_usd:
            raise BudgetExceeded(f"spend {usd(self.spent_usd)} > {usd(self.max_usd)}")

    def report(self) -> str:
        return (f"{self.calls} calls, {self.input_tokens:,} in / {self.output_tokens:,} out, "
                f"{usd(self.spent_usd)} of {usd(self.max_usd)}")


# ---------------------------------------------------------------------------
# Simulated runaway agent
# ---------------------------------------------------------------------------


def simulate(budget: TokenBudget, scenario: str) -> None:
    """A fake agent whose context grows by each tool result, as a real one would."""
    context = 6_000
    plan = {
        # A normal investigation: different tools, then done.
        "healthy": [("splunk_search", "src=10.0.4.22"), ("whois_lookup", "evil.example"),
                    ("nvd_cve_lookup", "CVE-2026-1234"), (None, None)],
        # The agent keeps re-running the same search because results look "incomplete".
        "stuck": [("splunk_search", "src=10.0.4.22")] * 10,
        # A prompt-injected page tells the agent to fetch ever-larger pages.
        "injected": [("fetch_url", f"https://attacker.example/page?{i}") for i in range(40)],
    }[scenario]

    try:
        for step, (tool_name, tool_args) in enumerate(plan, start=1):
            budget.record_llm_call(context, 400)
            if tool_name is None:
                print(f"   step {step}: final answer")
                break
            budget.record_tool_call(tool_name, tool_args)
            tool_output = 30_000 if scenario == "injected" else 3_000
            context += 400 + tool_output
            print(f"   step {step}: {tool_name}({tool_args}) -> context now {context:,} tokens")
        print(f"   finished: {budget.report()}")
    except BudgetExceeded as exc:
        print(f"   STOPPED: {exc}")
        print(f"   at stop: {budget.report()}")


def run_simulation() -> None:
    for scenario in ["healthy", "stuck", "injected"]:
        print(f"\nScenario: {scenario}")
        simulate(TokenBudget(model="gpt-6.1-sol"), scenario)
    print(
        "\nWhen a budget trips, fail closed: stop the agent, keep the partial work, and hand"
        "\nthe task to a human with the reason. Never silently retry with a bigger budget.\n"
    )


# ---------------------------------------------------------------------------
# Live LangChain agent with the budget enforced from a callback
# ---------------------------------------------------------------------------


def run_live(model_name: str) -> None:
    import os

    from dotenv import load_dotenv
    from langchain.agents import create_agent
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Add it to your environment or a .env file.")

    budget = TokenBudget(model=model_name, max_input_tokens=40_000, max_usd=0.05)

    class BudgetCallback(BaseCallbackHandler):
        raise_error = True  # LangChain swallows callback errors unless this is set

        def on_llm_end(self, response, **kwargs):
            for generations in response.generations:
                for gen in generations:
                    usage = getattr(getattr(gen, "message", None), "usage_metadata", None) or {}
                    cached = (usage.get("input_token_details") or {}).get("cache_read", 0)
                    budget.record_llm_call(usage.get("input_tokens", 0), usage.get("output_tokens", 0), cached)

        def on_tool_start(self, serialized, input_str, **kwargs):
            budget.record_tool_call(serialized.get("name", "tool"), input_str)

    @tool
    def lookup_cve(cve_id: str) -> str:
        """Return a short description of a CVE."""
        return f"{cve_id}: remote code execution in an example web framework. CVSS 9.8. Patch available."

    agent = create_agent(
        model=ChatOpenAI(model=model_name),
        tools=[lookup_cve],
        system_prompt="You are a vulnerability triage assistant. Be brief.",
    )
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "Look up CVE-2026-1234 and tell me if it is urgent."}]},
            config={"callbacks": [BudgetCallback()]},
        )
        print(result["messages"][-1].content)
    except BudgetExceeded as exc:
        print(f"STOPPED: {exc}")
    print(f"\nBudget: {budget.report()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Per-task token and cost ceilings for agents.")
    parser.add_argument("--live", action="store_true", help="run a real LangChain agent")
    parser.add_argument("--model", default="gpt-6-luna")
    args = parser.parse_args()
    if args.live:
        run_live(args.model)
    else:
        run_simulation()


if __name__ == "__main__":
    main()
