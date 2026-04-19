# eval/benchmark.py
#
# This is the evaluation harness.
# It takes any "agent function" and scores it against our 10 bug files.
#
# An agent function must have this signature:
#   def my_agent(code: str) -> str
# It receives the buggy Python code as a string,
# and must return a plain-English description of the bug.

import os
from eval.ground_truth2 import GROUND_TRUTH

BUGS_DIR = os.path.join(os.path.dirname(__file__), "bugs")


def load_bug_file(filename: str) -> str:
    """Read a bug file and return its contents as a string."""
    path = os.path.join(BUGS_DIR, filename)
    with open(path, "r") as f:
        return f.read()


def score_answer(bug_id: str, agent_answer: str) -> bool:
    """
    Check if the agent's answer is correct for a given bug.
    
    We do a simple keyword check: if any of the expected keywords
    appear in the agent's answer (case-insensitive), we count it correct.
    
    This is intentionally lenient — we want to measure whether the agent
    understood the bug, not whether it used exact wording.
    """
    truth = GROUND_TRUTH[bug_id]
    answer_lower = agent_answer.lower()
    
    for keyword in truth["keywords"]:
        if keyword.lower() in answer_lower:
            return True
    return False


def run_benchmark(agent_fn, verbose: bool = True) -> dict:
    """
    Run the agent function against all 10 bug files and return results.
    
    Returns a dict with:
      - score: float (0.0 to 1.0)
      - results: list of per-bug dicts
      - passed: int
      - total: int
    """
    results = []
    passed = 0
    total = len(GROUND_TRUTH)

    if verbose:
        print(f"\n{'='*50}")
        print("Running benchmark...")
        print(f"{'='*50}")

    for bug_id, truth in GROUND_TRUTH.items():
        filename = f"{bug_id}.py"
        code = load_bug_file(filename)

        # Call the agent
        try:
            agent_answer = agent_fn(code)
        except Exception as e:
            agent_answer = f"ERROR: {e}"

        correct = score_answer(bug_id, agent_answer)
        if correct:
            passed += 1

        result = {
            "bug_id": bug_id,
            "correct": correct,
            "agent_answer": agent_answer,
            "expected_description": truth["description"],
        }
        results.append(result)

        if verbose:
            status = "PASS" if correct else "FAIL"
            print(f"  [{status}] {bug_id}: {truth['description'][:55]}...")
            if not correct:
                # Show what the agent said, truncated
                print(f"         Agent said: {agent_answer[:80]}...")

    score = passed / total

    if verbose:
        print(f"\nScore: {passed}/{total} = {score:.0%}")
        print(f"{'='*50}\n")

    return {
        "score": score,
        "passed": passed,
        "total": total,
        "results": results,
    }
