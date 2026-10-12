# The metric that matters: cost per outcome, not cost per token.
#
#                          model + runtime + human review
#   cost per accepted fix = ------------------------------
#                                 acceptance rate
#
# The numerator is what one attempt really costs. Splunk's "agent tokenomics" article
# adds human review to the model bill. Dividing by the acceptance rate (this course's
# extension) turns cost per attempt into cost per accepted result: if only 60% of
# attempts are accepted, you need 1 / 0.6 = 1.67 attempts on average to get one good fix.
#
# This script:
#   1. Reproduces the Splunk example ($0.02 per task becomes about $3.02 per answer)
#   2. Shows why an "expensive" model can be cheaper per accepted fix
#   3. Prints a sensitivity grid so you can see which term dominates
#   4. Applies the same lens to benchmark scores (cost per solved task)
#
# Runs fully offline. All non-Splunk numbers are illustrative: replace them with
# measurements from your own workflow.
#
# Instructor: Omar Santos @santosomar

from dataclasses import dataclass

from token_math import usd


@dataclass
class Workflow:
    name: str
    model_cost: float  # USD of tokens per attempt
    runtime_cost: float  # sandboxes, scanners, CI minutes, vector DB, etc.
    review_share: float  # fraction of answers a human has to look at
    review_minutes: float  # minutes per reviewed answer
    hourly_rate: float  # loaded cost of the reviewer
    acceptance_rate: float  # fraction of attempts that end up accepted

    @property
    def review_cost(self) -> float:
        return self.review_share * (self.review_minutes / 60) * self.hourly_rate

    @property
    def cost_per_attempt(self) -> float:
        return self.model_cost + self.runtime_cost + self.review_cost

    @property
    def cost_per_accepted(self) -> float:
        return self.cost_per_attempt / self.acceptance_rate


def describe(w: Workflow) -> None:
    print(f"  {w.name}")
    print(f"    model {usd(w.model_cost)} + runtime {usd(w.runtime_cost)} + review {usd(w.review_cost)}"
          f" = {usd(w.cost_per_attempt)} per attempt")
    print(f"    / acceptance {w.acceptance_rate:.0%} = {usd(w.cost_per_accepted)} per accepted result")
    share = w.review_cost / w.cost_per_attempt if w.cost_per_attempt else 0
    print(f"    human review is {share:.1%} of the cost per attempt\n")


def section_splunk() -> None:
    print("1) The hidden term is people (Splunk example)")
    print("   $0.02 per task, 40% of answers need 15 minutes of review at $30/hour\n")
    w = Workflow("Cheap SOC agent", 0.02, 0.0, 0.40, 15, 30, 1.0)
    describe(w)


def section_cheap_vs_expensive() -> None:
    print("2) An 'expensive' model can be cheaper at the end (illustrative)")
    print("   Task: triage a scanner finding and propose a patch\n")
    cheap = Workflow("Small model", model_cost=0.03, runtime_cost=0.05, review_share=0.60,
                     review_minutes=20, hourly_rate=95, acceptance_rate=0.55)
    frontier = Workflow("Frontier model", model_cost=0.90, runtime_cost=0.05, review_share=0.15,
                        review_minutes=10, hourly_rate=95, acceptance_rate=0.90)
    describe(cheap)
    describe(frontier)
    ratio = frontier.model_cost / cheap.model_cost
    win = cheap.cost_per_accepted / frontier.cost_per_accepted
    print(f"   The frontier model's tokens cost {ratio:.0f}x more, yet each accepted fix costs"
          f" {win:.1f}x less.\n")


def section_sensitivity() -> None:
    print("3) Sensitivity: cost per accepted fix for a $0.20 model call, $95/hour reviewer, 15 min reviews")
    shares = [0.0, 0.1, 0.25, 0.5, 0.75]
    rates = [0.5, 0.7, 0.9, 0.99]
    header = "   review share | " + " | ".join(f"accept {r:.0%}".rjust(11) for r in rates)
    print(header)
    print("   " + "-" * (len(header) - 3))
    for s in shares:
        row = [Workflow("", 0.20, 0.0, s, 15, 95, r).cost_per_accepted for r in rates]
        print(f"   {s:>12.0%} | " + " | ".join(usd(c).rjust(11) for c in row))
    print("\n   Reading across a row: acceptance rate multiplies everything."
          "\n   Reading down a column: review share quickly dwarfs the model bill.\n")


def section_benchmark_lens() -> None:
    print("4) Same lens on benchmarks: cost to clear a backlog (illustrative)")
    print("   Artificial Analysis reports pass rates and the cost to run each eval. In production"
          "\n   every task the model does not solve lands on a human. A refusal (safety block) is"
          "\n   cheap to detect; a wrong patch costs a review plus the rework.\n")
    tasks = 120  # e.g. CWE-Bench-AA has 120 audit-and-patch tasks
    hourly = 95
    human_after_refusal = hourly * 30 / 60  # engineer picks the task up from scratch
    human_after_failure = hourly * 45 / 60  # review the bad patch, then fix it
    candidates = [
        # name, USD to run all tasks, pass rate, refusal rate
        ("Model A (frontier)", 260.0, 0.55, 0.00),
        ("Model B (mid-tier)", 70.0, 0.37, 0.00),
        ("Model C (cheap, cautious)", 25.0, 0.13, 0.57),
    ]
    print(f"   {'Model':<26} | {'Run cost':>9} | {'Pass':>5} | {'Refuse':>6} | {'$/solved':>9} | {'Backlog cost':>12}")
    print("   " + "-" * 82)
    for name, run_cost, pass_rate, refusal_rate in candidates:
        per_solved = run_cost / (tasks * pass_rate)
        failed = tasks * (1 - pass_rate - refusal_rate)
        backlog = run_cost + tasks * refusal_rate * human_after_refusal + failed * human_after_failure
        print(f"   {name:<26} | {usd(run_cost):>9} | {pass_rate:>5.0%} | {refusal_rate:>6.0%} |"
              f" {usd(per_solved):>9} | {usd(backlog):>12}")
    print("\n   Model B looks cheapest per solved task, but Model A clears the whole backlog for"
          "\n   the least money because fewer tasks fall through to people."
          "\n   Pick the model with the lowest cost per accepted outcome on YOUR tasks, then"
          "\n   route cheaper models to the steps where they match that acceptance rate.\n")


def main() -> None:
    section_splunk()
    section_cheap_vs_expensive()
    section_sensitivity()
    section_benchmark_lens()


if __name__ == "__main__":
    main()
