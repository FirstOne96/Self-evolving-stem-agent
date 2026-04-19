# stem/builder.py
#
# The Builder is Phase 3 of the stem loop.
# It takes the agent spec from the Designer and instantiates
# two agents: the generic baseline and the specialized agent.
# It also runs both against the benchmark so we get before/after scores.

import json
from agents.base_agent import GenericAgent, SpecializedAgent
from eval.strict_benchmark import run_strict_benchmark as run_benchmark


def run_builder(spec: dict, verbose: bool = True) -> dict:
    """
    Instantiate both agents from the spec and run them on the benchmark.

    Args:
        spec:    Output from run_designer()
        verbose: Whether to print progress

    Returns a dict with:
        generic_agent:     the unspecialized agent instance
        specialized_agent: the specialized agent instance
        baseline_result:   benchmark result for the generic agent
        specialized_result: benchmark result for the specialized agent
    """
    if verbose:
        print(f"\n[Builder] Instantiating agents...")
        print(f"  - Architecture : {spec.get('architecture')}")
        print(f"  - Tools        : {spec.get('tools')}")

    generic_agent     = GenericAgent()
    specialized_agent = SpecializedAgent(spec)

    # --- Baseline run (before specialization) ---
    if verbose:
        print(f"\n[Builder] Running BASELINE agent on benchmark...")

    baseline_result = run_benchmark(
        agent_fn=generic_agent.run,
        verbose=verbose,
    )

    # --- Specialized run (after specialization) ---
    if verbose:
        print(f"\n[Builder] Running SPECIALIZED agent on benchmark...")

    specialized_result = run_benchmark(
        agent_fn=specialized_agent.run,
        verbose=verbose,
    )

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