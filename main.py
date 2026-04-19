# main.py
#
# Entry point — run this with: python main.py
#
# This is the full stem agent loop:
#   Phase 1: Researcher  — figures out how QA agents are built
#   Phase 2: Designer    — writes its own system prompt and strategy
#   Phase 3: Builder     — instantiates both agents, runs the benchmark
#   Phase 4: Evaluator   — decides to stop or loop back with feedback
#
# At the end, logs/evolution.json contains every decision made,
# and the terminal shows the before/after score comparison.

import json
import os
from datetime import datetime

from config import MAX_EVOLUTION_ROUNDS, SUCCESS_THRESHOLD
from stem.researcher import run_researcher
from stem.designer   import run_designer
from stem.builder    import run_builder
from stem.evaluator  import run_evaluator

DOMAIN = "QA / Bug Finding"
LOG_PATH = "logs/evolution.json"


def main():
    os.makedirs("logs", exist_ok=True)

    print("\n" + "="*60)
    print("  STEM AGENT — starting evolution")
    print(f"  Domain    : {DOMAIN}")
    print(f"  Max rounds: {MAX_EVOLUTION_ROUNDS}")
    print(f"  Threshold : {SUCCESS_THRESHOLD:.0%}")
    print("="*60)

    evolution_log = {
        "domain":     DOMAIN,
        "started_at": datetime.now().isoformat(),
        "rounds":     [],
        "final":      None,
    }

    # ── Phase 1: Research (done once — domain doesn't change) ──────────
    domain_map = run_researcher(DOMAIN)
    with open("logs/domain_map.json", "w") as f:
        json.dump(domain_map, f, indent=2)

    # State carried across rounds
    previous_score    = None
    previous_prompt   = None
    previous_failures = None

    best_build_result = None
    best_score        = 0.0

    # ── Evolution loop ──────────────────────────────────────────────────
    for round_num in range(1, MAX_EVOLUTION_ROUNDS + 1):
        print(f"\n{'─'*60}")
        print(f"  ROUND {round_num}")
        print(f"{'─'*60}")

        # Phase 2: Design
        spec = run_designer(
            domain_map=domain_map,
            previous_score=previous_score,
            previous_prompt=previous_prompt,
            previous_failures=previous_failures,
        )
        with open(f"logs/agent_spec_round{round_num}.json", "w") as f:
            json.dump(spec, f, indent=2)

        # Phase 3: Build + score
        build_result = run_builder(spec)

        # Phase 4: Evaluate
        eval_result = run_evaluator(
            build_result=build_result,
            round_number=round_num,
            max_rounds=MAX_EVOLUTION_ROUNDS,
        )

        # Log this round
        round_log = {
            "round":              round_num,
            "architecture":       spec.get("architecture"),
            "system_prompt":      spec.get("system_prompt"),
            "designer_reasoning": spec.get("reasoning"),
            "baseline_score":     eval_result["baseline_score"],
            "specialized_score":  eval_result["score"],
            "failed_bugs":        eval_result["failed_bugs"],
            "missed_patterns":    eval_result["missed_patterns"],
            "decision":           eval_result["decision"],
            "stop_reason":        eval_result["stop_reason"],
            "loop_reason":        eval_result["loop_reason"],
        }
        evolution_log["rounds"].append(round_log)

        # Track best result across all rounds
        if eval_result["score"] > best_score:
            best_score        = eval_result["score"]
            best_build_result = build_result

        # Update state for next round (if looping)
        previous_score    = eval_result["score"]
        previous_prompt   = spec.get("system_prompt")
        previous_failures = eval_result["failed_bugs"]

        if eval_result["decision"] == "STOP":
            break

    # ── Final summary ───────────────────────────────────────────────────
    baseline_score = best_build_result["baseline_result"]["score"]
    final_score    = best_score
    delta          = final_score - baseline_score
    sign           = "+" if delta >= 0 else ""
    rounds_taken   = len(evolution_log["rounds"])

    evolution_log["final"] = {
        "rounds_taken":    rounds_taken,
        "baseline_score":  baseline_score,
        "final_score":     final_score,
        "improvement":     delta,
        "completed_at":    datetime.now().isoformat(),
    }

    with open(LOG_PATH, "w") as f:
        json.dump(evolution_log, f, indent=2)

    print("\n" + "="*60)
    print("  EVOLUTION COMPLETE")
    print("="*60)
    print(f"  Rounds taken      : {rounds_taken}")
    print(f"  Baseline score    : {baseline_score:.0%}  (generic agent, no specialization)")
    print(f"  Final score       : {final_score:.0%}  (specialized agent)")
    print(f"  Improvement       : {sign}{delta:.0%}")
    print(f"  Full log saved to : {LOG_PATH}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()