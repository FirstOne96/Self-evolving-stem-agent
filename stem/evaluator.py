# stem/evaluator.py
from config import SUCCESS_THRESHOLD


def run_evaluator(build_result, round_number, max_rounds, verbose=True):
    specialized_result = build_result["specialized_result"]
    baseline_result    = build_result["baseline_result"]
    score              = specialized_result["score"]
    baseline_score     = baseline_result["score"]

    # Works with BOTH benchmark formats:
    # - keyword benchmark: results have "correct" (bool)
    # - strict benchmark:  results have "points" (0/1/2)
    def is_failed(r):
        if "correct" in r:
            return not r["correct"]
        if "points" in r:
            return r["points"] < 2  # 0 or 1 = not fully correct
        return False

    failed_bugs = [
        r["bug_id"]
        for r in specialized_result["results"]
        if is_failed(r)
    ]

    missed_patterns = _summarize_failures(specialized_result["results"])

    if verbose:
        print(f"\n[Evaluator] Round {round_number}/{max_rounds}")
        print(f"  Score     : {score:.0%}  (threshold: {SUCCESS_THRESHOLD:.0%})")
        print(f"  Baseline  : {baseline_score:.0%}")
        print(f"  Failed    : {failed_bugs if failed_bugs else 'none'}")

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
            f"Still missing: {', '.join(failed_bugs)}. Pattern: {missed_patterns}"
        )

    if verbose:
        print(f"  Decision  : {decision} — {stop_reason or loop_reason}")

    return {
        "decision":        decision,
        "score":           score,
        "baseline_score":  baseline_score,
        "failed_bugs":     failed_bugs,
        "stop_reason":     stop_reason,
        "loop_reason":     loop_reason,
        "missed_patterns": missed_patterns,
    }


def _summarize_failures(results):
    def is_failed(r):
        if "correct" in r:   return not r["correct"]
        if "points"  in r:   return r["points"] < 2
        return False

    failed = [r for r in results if is_failed(r)]
    if not failed:
        return "none"
    lines = []
    for r in failed:
        lines.append(
            f"{r['bug_id']}: agent said '{r['agent_answer'][:80]}' "
            f"but expected '{r['expected_description']}'"
        )
    return " | ".join(lines)