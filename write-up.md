# Write-up

*JetBrains Applied AI Engineering — Internship Task*

## 1. Approach

I built a meta-agent whose job is to research how bug-finding agents work and then grow into one. The system runs a four-phase evolution loop until the agent is good enough to stop — the same way a stem cell reads signals from its environment and specializes into whatever the body needs.

The benchmark was defined before any agent code was written. This order matters: defining what success looks like first prevents the evaluation from being shaped around what the agent already does well.

Two model tiers are used deliberately. `gpt-4o-mini` runs as the agent under test — it is cheaper and has a real precision gap when prompted vaguely. `gpt-4o` handles research, design, and judging. Scoring uses an LLM-as-judge rather than keyword matching, grading each answer on correctness and precision separately.

## 2. Benchmark Design

The benchmark is 20 Python functions, each containing exactly one bug. After two failed benchmark iterations (described in section 5), the final design scores on two dimensions: whether the agent found the bug, and whether it named the exact wrong expression.

This two-axis design is the key architectural decision. A generic "find the bug" prompt reliably scores 1/2 — it identifies the right area but describes it vaguely ("the loop is wrong"). A specialized prompt that forces step-by-step tracing scores 2/2 by driving the model toward expression-level specificity ("range(1, len(nums)) should be range(len(nums))"). The gap between those two is structural, not lucky — it shows up consistently across bug types.

## 3. Results

The stem loop ran one round and stopped. Baseline 88%, specialized 100%, improvement +12%.

Every point of improvement came from the precision dimension. All 20 bugs were identified correctly by both agents, but 5 were described vaguely by the generic agent and precisely by the specialized one after the Designer produced a trace-focused system prompt. The 5 vague bugs from the baseline run — `bug_01`, `bug_03`, `bug_06`, `bug_10`, `bug_14` — were ones where the generic agent correctly identified the category of bug but did not name the exact expression. For example on `bug_01` it said "the loop starts at index 1 instead of 0" without stating "range(1, len(nums)) should be range(len(nums))". The specialized agent named the expression in all five cases.

## 4. What Surprised Me

The precision dimension was more powerful than expected. When the eval scored only on correctness, both agents scored near 100% and there was nothing for the stem loop to improve. Adding precision as a second axis immediately revealed a structural gap between vague and specific prompts — one that exists consistently across all bug types.

The Designer found the right fix without being told what the scoring dimensions were. The Designer prompt does not mention "correctness" or "precision" — it just gets told which bugs failed and asked to fix them. It independently inferred from the failure descriptions that the problem was imprecision, and produced a system prompt with explicit tracing instructions. The stem cell read the signal correctly.

Earlier attempts revealed something more interesting. When the Designer prompt was more explicit about the scoring criteria, the Designer would produce system prompts that were *too* well-targeted — essentially hardcoding the scoring dimensions rather than reasoning from the domain. The current version, which only shows the Designer the failure descriptions, produces more genuinely emergent specialization.

## 5. What Failed

**Two benchmark iterations before the final design.** The first benchmark (10 classic bugs, keyword scoring) was passed at 90%+ by both agents — frontier models pattern-match to classic Python bugs without needing to reason. The second (15 bugs including harder trace-required ones) had the same problem. The fix was not harder bugs but a different scoring axis. Precision separates agents that reason from agents that pattern-match, regardless of bug difficulty.

**The multi-round recovery loop was never exercised in the final configuration.** The Designer produced a good-enough system prompt in round 1 every time. This means the most interesting part of the architecture — the Designer self-correcting from failure feedback across multiple rounds — was demonstrated in early iterations but not in the final clean run. The loop works (demonstrated in an earlier run where round 1 scored 40% and round 2 recovered to 70%), but the final benchmark is too easy to require it.

**The Designer's tool recommendations are mostly irrelevant.** It consistently suggests Selenium and SonarQube — real QA tools, but useless for a pure code reasoning task. The Researcher correctly identifies these as important QA tools, and the Designer faithfully includes them. A domain map with a "task type" field would let the Designer filter by relevance. This is a cosmetic issue for now but would matter in a real deployment.

## 6. What I Would Do With More Time

**Force multi-round evolution.** Lower the threshold to 75% and use a benchmark hard enough that round 1 reliably falls short. The self-correction loop is the most interesting part of the system and it should be demonstrated in the final run, not just in early iterations.

**Two-domain test.** Run the stem loop on Security (CTF challenges) and verify the produced agent is structurally different from the QA one. The stem cell claim is "different input, different output" — one domain is a proof of concept, two would be a proof of principle.

**Feedback to the Researcher.** Currently the Evaluator's failure patterns only reach the Designer. A stronger loop would update the domain map too, so persistent gaps would trigger deeper research rather than just prompt adjustments.

**Real-world bug corpus.** Pull bugs from open-source Python repositories with actual commit history. These exist in multi-file context, are not in any model's training data verbatim, and would require genuine reasoning rather than pattern recognition.

**Persist the specialized agent.** The final spec is saved to `logs/agent_spec_round1.json`. A production version would load this directly for deployment without re-running the evolution loop — decoupling specialization from execution.
