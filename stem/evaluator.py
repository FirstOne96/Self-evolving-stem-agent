# stem/evaluator.py
from config import SUCCESS_THRESHOLD


def run_evaluator(build_result, round_number, max_rounds, verbose=True):
    specialized = build_result["specialized_result"]
    baseline    = build_result["baseline_result"]
    score       = specialized["score"]
    base_score  = baseline["score"]

    # Bugs where agent was correct but vague (precision=0) — Designer's target
    vague_bugs = [
        r["bug_id"] for r in specialized["results"]
        if r.get("correctness") == 1 and r.get("precision") == 0
    ]
    # Bugs where agent was just wrong
    wrong_bugs = [
        r["bug_id"] for r in specialized["results"]
        if r.get("correctness") == 0
    ]
    failed_bugs = vague_bugs + wrong_bugs

    missed_patterns = _summarize_failures(specialized["results"])

    if verbose:
        print(f"\n[Evaluator] Round {round_number}/{max_rounds}")
        print(f"  Score     : {score:.0%}  (threshold: {SUCCESS_THRESHOLD:.0%})")
        print(f"  Baseline  : {base_score:.0%}")
        print(f"  Vague     : {vague_bugs if vague_bugs else 'none'}  (correct but imprecise)")
        print(f"  Wrong     : {wrong_bugs if wrong_bugs else 'none'}")

    if score >= SUCCESS_THRESHOLD:
        decision    = "STOP"
        stop_reason = f"Score {score:.0%} meets threshold {SUCCESS_THRESHOLD:.0%}"
        loop_reason = None
    elif round_number >= max_rounds:
        decision    = "STOP"
        stop_reason = f"Reached max rounds ({max_rounds}) — best score {score:.0%}"
        loop_reason = None
    else:
        decision    = "LOOP"
        stop_reason = None
        loop_reason = (
            f"Score {score:.0%} below threshold {SUCCESS_THRESHOLD:.0%}. "
            f"Vague (correct but imprecise): {vague_bugs}. "
            f"Wrong: {wrong_bugs}. "
            f"Pattern: {missed_patterns}"
        )

    if verbose:
        print(f"  Decision  : {decision} — {stop_reason or loop_reason[:80]}")

    return {
        "decision":        decision,
        "score":           score,
        "baseline_score":  base_score,
        "failed_bugs":     failed_bugs,
        "vague_bugs":      vague_bugs,
        "wrong_bugs":      wrong_bugs,
        "stop_reason":     stop_reason,
        "loop_reason":     loop_reason,
        "missed_patterns": missed_patterns,
    }


def _summarize_failures(results):
    lines = []
    for r in results:
        c = r.get("correctness", 0)
        p = r.get("precision",   0)
        if c == 1 and p == 0:
            lines.append(
                f"{r['bug_id']}: correct but vague — agent said "
                f"'{r['agent_answer'][:60]}' but needed to name '{r['exact_fault'][:60]}'"
            )
        elif c == 0:
            lines.append(
                f"{r['bug_id']}: wrong — agent said '{r['agent_answer'][:60]}' "
                f"expected '{r['expected_description'][:60]}'"
            )
    return " | ".join(lines) if lines else "none"