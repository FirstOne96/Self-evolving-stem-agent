# eval/strict_benchmark.py
#
# LLM-as-judge scorer. Uses JUDGE_MODEL (gpt-4o) to evaluate
# whether the agent's answer is correct, not just whether keywords match.
#
# Scores: 2 = correct + explained, 1 = right area but vague, 0 = wrong/missing

import os
from openai import OpenAI
from config import OPENAI_API_KEY, JUDGE_MODEL
from eval.ground_truth2 import GROUND_TRUTH

client   = OpenAI(api_key=OPENAI_API_KEY)
BUGS_DIR = os.path.join(os.path.dirname(__file__), "bugs")

JUDGE_PROMPT = """You are evaluating whether an AI correctly identified a Python bug.

Expected bug: {expected}
Agent's answer: {answer}

Score:
2 = correctly identifies the specific bug (right line, right reason)
1 = partially correct (right area but vague or missing exact cause)
0 = wrong, missing, or too vague

Reply with ONLY the number 0, 1, or 2."""


def judge_answer(expected: str, agent_answer: str) -> int:
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            expected=expected, answer=agent_answer
        )}],
        temperature=0,
        max_tokens=5,
    )
    raw = response.choices[0].message.content.strip()
    try:
        return min(max(int(raw[0]), 0), 2)
    except:
        return 0


def run_strict_benchmark(agent_fn, verbose=True) -> dict:
    results = []
    total_points = 0
    max_points   = len(GROUND_TRUTH) * 2

    if verbose:
        print(f"\n{'='*50}")
        print("Running STRICT benchmark (LLM-as-judge)...")
        print(f"{'='*50}")

    for bug_id, truth in GROUND_TRUTH.items():
        path = os.path.join(BUGS_DIR, f"{bug_id}.py")
        with open(path) as f:
            code = f.read()

        try:
            agent_answer = agent_fn(code)
        except Exception as e:
            agent_answer = f"ERROR: {e}"

        points = judge_answer(truth["description"], agent_answer)
        total_points += points
        label = ["FAIL", "PART", "PASS"][points]
        results.append({
            "bug_id":               bug_id,
            "points":               points,
            "agent_answer":         agent_answer,
            "expected_description": truth["description"],
        })

        if verbose:
            print(f"  [{label}] {bug_id} ({points}/2): {truth['description'][:50]}...")
            if points < 2:
                print(f"         Agent: {agent_answer[:80]}...")

    score = total_points / max_points
    if verbose:
        print(f"\nStrict score: {total_points}/{max_points} = {score:.0%}")
        print(f"{'='*50}\n")

    return {
        "score":        score,
        "total_points": total_points,
        "max_points":   max_points,
        "results":      results,
    }