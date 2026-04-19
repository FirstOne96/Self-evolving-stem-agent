# stem/designer.py
#
# Phase 2 of the stem loop.
# Reads the domain map from the Researcher and writes a concrete agent spec:
# a system prompt, architecture choice, reasoning strategy, and tool list.
# The key thing it produces is a system prompt that forces precise bug identification
# rather than vague descriptions — that's what closes the scoring gap.
#
# On the first round it only has the domain map to work with.
# On subsequent rounds it also gets the list of bugs that were vague last time,
# so it can adjust the system prompt specifically for those.

import json
from openai import OpenAI
from config import OPENAI_API_KEY, JUDGE_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

DESIGNER_SYSTEM_PROMPT = """You are an AI agent architect.
You receive a domain research map and design a system prompt for a bug-finding agent.

Respond with valid JSON only. No markdown outside the JSON.

{
  "system_prompt": "<the complete system prompt>",
  "architecture": "<architecture name>",
  "strategy": "<per-problem reasoning steps>",
  "tools": ["<tool1>"],
  "reasoning": "<why these choices, referencing research>"
}

The agent receives a Python code snippet and must identify the one bug in it.
The agent is scored on TWO dimensions:
  1. CORRECTNESS — did it identify the right bug?
  2. PRECISION    — did it name the exact wrong expression or line?

The generic baseline scores poorly on PRECISION because it describes bugs vaguely
("the loop is wrong") without naming the exact expression ("range(1, len(nums))").

Your system prompt must force the agent to:
  - Trace through the code line by line before concluding
  - Name the exact expression, variable, or line that is wrong
  - Explain specifically why that expression fails
  - State what the expression should be instead

Do NOT tell the agent to generate test cases, write QA reports, or suggest refactors."""

DESIGNER_USER_PROMPT = """Design a system prompt for a Python bug-finding agent.

DOMAIN RESEARCH:
{domain_map}

Previous score: {previous_score}
Previous system prompt: {previous_prompt}
Bugs where precision was low (correct area, vague explanation): {previous_failures}

The scoring gap between generic and specialized agents comes from PRECISION.
The generic agent says "the condition is inverted" — scores 1/2.
The specialized agent says "n <= 0 should be n > 0" — scores 2/2.

Design a system prompt that forces precise, expression-level identification of bugs.
If there was a previous attempt, change the reasoning strategy specifically to
target the bugs that were vague or wrong last time."""


def run_designer(domain_map, previous_score=None, previous_prompt=None,
                 previous_failures=None, verbose=True):
    """
    Generate an agent spec from the domain map.

    On the first call previous_score/prompt/failures are all None.
    On retry rounds they contain what went wrong last time so the
    Designer can adjust its system prompt specifically for those bugs.

    Returns a dict with: system_prompt, architecture, strategy, tools, reasoning.
    """
    if verbose:
        print(f"\n[Designer] Designing agent for domain: '{domain_map.get('domain')}'...")
        if previous_score is not None:
            print(f"[Designer] Previous score {previous_score:.0%} — targeting precision gap...")

    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": DESIGNER_SYSTEM_PROMPT},
            {"role": "user",   "content": DESIGNER_USER_PROMPT.format(
                domain_map=json.dumps(domain_map, indent=2),
                previous_score=f"{previous_score:.0%}" if previous_score is not None else "N/A (first attempt)",
                previous_prompt=previous_prompt or "N/A",
                previous_failures=json.dumps(previous_failures) if previous_failures else "N/A",
            )},
        ],
        temperature=0.4,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            spec = json.loads(raw.strip())
        else:
            raise ValueError(f"Designer returned invalid JSON:\n{raw}")

    if verbose:
        print(f"[Designer] Done.")
        print(f"  - Architecture: {spec.get('architecture')}")
        print(f"  - Tools: {spec.get('tools')}")
        print(f"  - Prompt length: {len(spec.get('system_prompt', ''))} chars")
        print(f"  - Reasoning: {spec.get('reasoning', '')[:100]}...")

    return spec