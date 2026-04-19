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
You receive a domain research map and design a system prompt for a specialized agent in that domain.

Respond with valid JSON only. No markdown outside the JSON.

{
  "system_prompt": "<the complete system prompt>",
  "architecture": "<architecture name>",
  "strategy": "<per-problem reasoning steps>",
  "tools": ["<tool1>"],
  "reasoning": "<why these choices, referencing the domain research>"
}

Your goal is to build an agent that performs optimally based on the failure modes and best practices identified in the research.
If provided with failure feedback from a previous run, adjust your strategy and system prompt specifically to fix those exact failures."""

DESIGNER_USER_PROMPT = """Design a system prompt for an agent operating in the following domain.

DOMAIN RESEARCH:
{domain_map}

Previous score: {previous_score}
Previous system prompt: {previous_prompt}
Failed or vague outputs from previous run: {previous_failures}

Analyze the domain research to determine the optimal architecture and prompting strategy. Pay close attention to the recommended approaches and known failure modes.
If there was a previous attempt, you MUST change the system prompt and reasoning strategy to fix the specific failures provided."""


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