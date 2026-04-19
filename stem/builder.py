# stem/builder.py
#
# Phase 3 of the stem loop.
# Takes the agent spec from the Designer, creates both agents,
# runs them on the benchmark, and returns the results.
# The baseline (generic) run and the specialized run happen here
# so we can compare them directly in the same round.

from agents.base_agent import GenericAgent, SpecializedAgent
from eval.benchmark import run_benchmark


def run_builder(spec, verbose=True):
    """
    Instantiate both agents from the spec and run them on the benchmark.

    The generic agent always uses the same vague prompt — it's our baseline.
    The specialized agent uses the system prompt the Designer just wrote.
    Running both in the same round means the only variable is the system prompt.

    Returns a dict with the two agent instances and their benchmark results.
    """
    if verbose:
        print(f"\n[Builder] Instantiating agents...")
        print(f"  - Architecture : {spec.get('architecture')}")
        print(f"  - Tools        : {spec.get('tools')}")

    generic_agent     = GenericAgent()
    specialized_agent = SpecializedAgent(spec)

    if verbose:
        print(f"\n[Builder] Running BASELINE agent on benchmark...")

    baseline_result = run_benchmark(agent_fn=generic_agent.run, verbose=verbose)

    if verbose:
        print(f"\n[Builder] Running SPECIALIZED agent on benchmark...")

    specialized_result = run_benchmark(agent_fn=specialized_agent.run, verbose=verbose)

    if verbose:
        delta = specialized_result["score"] - baseline_result["score"]
        sign  = "+" if delta >= 0 else ""
        print(f"\n[Builder] Results:")
        print(f"  Baseline score    : {baseline_result['score']:.0%}")
        print(f"  Specialized score : {specialized_result['score']:.0%}")
        print(f"  Improvement       : {sign}{delta:.0%}")

    return {
        "generic_agent":      generic_agent,
        "specialized_agent":  specialized_agent,
        "baseline_result":    baseline_result,
        "specialized_result": specialized_result,
    }