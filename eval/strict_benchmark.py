# eval/strict_benchmark.py
#
# Two-dimension LLM-as-judge scorer.
#
# Every answer is scored on TWO axes, each 0 or 1:
#   correctness  — did the agent identify the right bug?
#   precision    — did it name the exact faulty expression/line?
#
# Max score per bug = 2. Total max = 40 (20 bugs × 2).
# Final score = total / 40 as a float 0.0–1.0.
#
# WHY TWO DIMENSIONS:
# A generic "find the bug" prompt often scores 1/2 — it identifies
# the right area but gives a vague explanation ("the loop is wrong").
# A specialized step-by-step trace prompt scores 2/2 because it is
# forced to name the exact expression and explain why it fails.
# This creates a reliable gap between generic and specialized agents.

import os
from openai import OpenAI
from config import OPENAI_API_KEY, JUDGE_MODEL
from eval.ground_truth import GROUND_TRUTH

client   = OpenAI(api_key=OPENAI_API_KEY)
BUGS_DIR = os.path.join(os.path.dirname(__file__), "bugs")

JUDGE_PROMPT = """You are evaluating an AI agent's answer about a Python bug.

Bug description (what the bug actually is):
{description}

Exact fault (the precise expression that is wrong):
{exact_fault}

Agent's answer:
{answer}

Score the answer on TWO dimensions. Reply with ONLY two digits separated by a space, e.g. "1 0" or "1 1" or "0 0".

Dimension 1 — CORRECTNESS (0 or 1):
  1 = the agent correctly identified what the bug is
  0 = wrong, missing, or fundamentally misunderstood

Dimension 2 — PRECISION (0 or 1):
  1 = the agent named the specific expression, line, or variable that is wrong
      (e.g. "range(1, len(nums))", "lst[len(lst)]", "return a", "i - 1")
  0 = vague — described the general area but didn't pinpoint the exact fault

Reply format: just two digits and a space, nothing else. Example: "1 0"
"""


def judge_answer(bug_id: str, agent_answer: str) -> tuple[int, int]:
    """Returns (correctness, precision) each 0 or 1."""
    truth = GROUND_TRUTH[bug_id]
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            description=truth["description"],
            exact_fault=truth["exact_fault"],
            answer=agent_answer,
        )}],
        temperature=0,
        max_tokens=10,
    )
    raw = response.choices[0].message.content.strip()
    try:
        parts = raw.split()
        return int(parts[0]), int(parts[1])
    except:
        return 0, 0


def run_strict_benchmark(agent_fn, verbose=True) -> dict:
    results        = []
    total_points   = 0
    max_points     = len(GROUND_TRUTH) * 2   # 2 points per bug

    if verbose:
        print(f"\n{'='*56}")
        print(f"Running benchmark ({len(GROUND_TRUTH)} bugs, 2 pts each)...")
        print(f"{'='*56}")

    for bug_id, truth in GROUND_TRUTH.items():
        path = os.path.join(BUGS_DIR, f"{bug_id}.py")
        with open(path) as f:
            code = f.read()

        try:
            agent_answer = agent_fn(code)
        except Exception as e:
            agent_answer = f"ERROR: {e}"

        correctness, precision = judge_answer(bug_id, agent_answer)
        points = correctness + precision
        total_points += points

        labels = {(1,1): "PASS", (1,0): "VAGUE", (0,0): "FAIL", (0,1): "FAIL"}
        label  = labels.get((correctness, precision), "FAIL")

        results.append({
            "bug_id":        bug_id,
            "points":        points,
            "correctness":   correctness,
            "precision":     precision,
            "agent_answer":  agent_answer,
            "expected_description": truth["description"],
            "exact_fault":   truth["exact_fault"],
        })

        if verbose:
            print(f"  [{label:5s}] {bug_id} ({points}/2 — C:{correctness} P:{precision}): "
                  f"{truth['description'][:45]}...")
            if points < 2:
                print(f"           Agent: {agent_answer[:80].strip()}...")

    score = total_points / max_points

    # Summary breakdown
    passed  = sum(1 for r in results if r["points"] == 2)
    vague   = sum(1 for r in results if r["correctness"] == 1 and r["precision"] == 0)
    failed  = sum(1 for r in results if r["correctness"] == 0)

    if verbose:
        print(f"\n  Score  : {total_points}/{max_points} = {score:.0%}")
        print(f"  Full   : {passed}  |  Vague: {vague}  |  Wrong: {failed}")
        print(f"{'='*56}\n")

    return {
        "score":        score,
        "total_points": total_points,
        "max_points":   max_points,
        "passed":       passed,
        "vague":        vague,
        "failed":       failed,
        "results":      results,
    }