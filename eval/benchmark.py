# eval/benchmark.py
#
# The main benchmark runner. Takes any agent function, runs it against
# all 20 bug files, and returns a score broken down by correctness and precision.
#
# Scoring works on two axes (0 or 1 each, so max 2 points per bug):
#   correctness — did the agent identify the right bug?
#   precision   — did it name the exact wrong expression or line?
#
# The two-axis design is important: a generic prompt tends to score 1/2
# (right area, vague explanation). A specialized trace prompt scores 2/2
# by forcing the model to name the exact expression. That gap is what we measure.

import os
from openai import OpenAI
from config import OPENAI_API_KEY, JUDGE_MODEL
from eval.ground_truth import GROUND_TRUTH

client   = OpenAI(api_key=OPENAI_API_KEY)
BUGS_DIR = os.path.join(os.path.dirname(__file__), "bugs")

# the judge prompt asks for two scores on one line, e.g. "1 0" or "1 1"
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


def judge_answer(bug_id, agent_answer):
    """
    Ask GPT-4o to score one agent answer on correctness and precision.
    Returns a tuple (correctness, precision) where each is 0 or 1.
    Falls back to (0, 0) if the model returns something unparseable.
    """
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
    except Exception:
        return 0, 0


def run_benchmark(agent_fn, verbose=True):
    """
    Run agent_fn against all 20 bug files and return a results dict.

    agent_fn should accept a string (the buggy code) and return a string (the explanation).

    The returned dict has:
      score        — float 0.0-1.0 (total points / max points)
      total_points — raw points scored
      max_points   — maximum possible (20 bugs * 2 = 40)
      passed       — bugs where agent scored 2/2
      vague        — bugs where agent was correct but imprecise (1/2)
      failed       — bugs where agent was wrong (0/2)
      results      — list of per-bug dicts with full breakdown
    """
    results      = []
    total_points = 0
    max_points   = len(GROUND_TRUTH) * 2

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

        # label for display: PASS = full marks, VAGUE = right but imprecise, FAIL = wrong
        label_map = {(1, 1): "PASS", (1, 0): "VAGUE", (0, 0): "FAIL", (0, 1): "FAIL"}
        label = label_map.get((correctness, precision), "FAIL")

        results.append({
            "bug_id":               bug_id,
            "points":               points,
            "correctness":          correctness,
            "precision":            precision,
            "agent_answer":         agent_answer,
            "expected_description": truth["description"],
            "exact_fault":          truth["exact_fault"],
        })

        if verbose:
            print(f"  [{label:5s}] {bug_id} ({points}/2 — C:{correctness} P:{precision}): "
                  f"{truth['description'][:45]}...")
            if points < 2:
                print(f"           Agent: {agent_answer[:80].strip()}...")

    score  = total_points / max_points
    passed = sum(1 for r in results if r["points"] == 2)
    vague  = sum(1 for r in results if r["correctness"] == 1 and r["precision"] == 0)
    failed = sum(1 for r in results if r["correctness"] == 0)

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