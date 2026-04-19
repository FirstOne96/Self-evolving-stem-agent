# main.py
#
# Entry point — run with: python main.py
#
# Runs the full stem agent evolution loop:
#   Phase 1: Researcher  — figures out how QA agents are typically built
#   Phase 2: Designer    — writes its own system prompt based on that research
#   Phase 3: Builder     — runs both the generic and specialized agent on the benchmark
#   Phase 4: Evaluator   — decides to stop or loop back with feedback on what failed
#
# Everything gets logged to logs/evolution.json so you can see every decision the
# stem agent made across all rounds. That's also the file to attach to the write-up.

import json
import os
from datetime import datetime

from config import MAX_EVOLUTION_ROUNDS, SUCCESS_THRESHOLD
from stem.researcher import run_researcher
from stem.designer   import run_designer
from stem.builder    import run_builder
from stem.evaluator  import run_evaluator

DOMAIN   = "QA / Bug Finding"
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

    # research happens once — the domain doesn't change between rounds
    domain_map = run_researcher(DOMAIN)
    with open("logs/domain_map.json", "w") as f:
        json.dump(domain_map, f, indent=2)

    # these get updated after each round and passed to the Designer on the next one
    previous_score    = None
    previous_prompt   = None
    previous_failures = None

    best_build_result = None
    best_score        = 0.0

    for round_num in range(1, MAX_EVOLUTION_ROUNDS + 1):
        print(f"\n{'─'*60}")
        print(f"  ROUND {round_num}")
        print(f"{'─'*60}")

        spec = run_designer(
            domain_map=domain_map,
            previous_score=previous_score,
            previous_prompt=previous_prompt,
            previous_failures=previous_failures,
        )
        with open(f"logs/agent_spec_round{round_num}.json", "w") as f:
            json.dump(spec, f, indent=2)

        build_result = run_builder(spec)

        eval_result = run_evaluator(
            build_result=build_result,
            round_number=round_num,
            max_rounds=MAX_EVOLUTION_ROUNDS,
        )

        # log everything about this round so we can trace the evolution later
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

        if eval_result["score"] > best_score:
            best_score        = eval_result["score"]
            best_build_result = build_result

        # pass failure info to the Designer for the next round (if there is one)
        previous_score    = eval_result["score"]
        previous_prompt   = spec.get("system_prompt")
        previous_failures = eval_result["failed_bugs"]

        if eval_result["decision"] == "STOP":
            break

    baseline_score = best_build_result["baseline_result"]["score"]
    final_score    = best_score
    delta          = final_score - baseline_score
    sign           = "+" if delta >= 0 else ""
    rounds_taken   = len(evolution_log["rounds"])

    evolution_log["final"] = {
        "rounds_taken":   rounds_taken,
        "baseline_score": baseline_score,
        "final_score":    final_score,
        "improvement":    delta,
        "completed_at":   datetime.now().isoformat(),
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