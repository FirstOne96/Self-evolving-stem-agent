# stem/designer.py
import json
from openai import OpenAI
from config import OPENAI_API_KEY, JUDGE_MODEL as MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

DESIGNER_SYSTEM_PROMPT = """You are an AI agent architect.
You receive a domain research map and design a concrete agent configuration.

You must respond with valid JSON only. No markdown, no explanation outside the JSON.

{
  "system_prompt": "<complete system prompt the specialized agent will use>",
  "architecture": "<chosen architecture name>",
  "strategy": "<step-by-step instructions the agent follows per problem>",
  "tools": ["<tool1>", "<tool2>"],
  "reasoning": "<why these choices, referencing the research>"
}

CRITICAL rules for the system_prompt you write:
- The agent receives one Python code snippet and must describe the bug already present in it
- The agent must NOT generate test cases, test plans, or refactoring suggestions
- The agent must identify: the specific wrong line/expression, why it fails, what it should be
- The system prompt must directly address the failure modes from the research
- Keep the response focused on bug identification, not QA process"""

DESIGNER_USER_PROMPT = """Based on this domain research, design a specialized bug-finding agent.

DOMAIN MAP:
{domain_map}

Previous attempt score (if any): {previous_score}
Previous system prompt (if any): {previous_prompt}
What failed last time (if any): {previous_failures}

The agent's ONLY job: given a Python function, identify the one bug in it.
Output must be a bug description — not test cases, not a QA process, not refactoring advice.

If there was a previous attempt, make meaningful changes targeting what failed specifically."""


def run_designer(domain_map, previous_score=None, previous_prompt=None,
                 previous_failures=None, verbose=True):
    if verbose:
        print(f"\n[Designer] Designing agent for domain: '{domain_map.get('domain')}'...")
        if previous_score is not None:
            print(f"[Designer] Previous score was {previous_score:.0%} — improving...")

    response = client.chat.completions.create(
        model=MODEL,
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
            if raw.startswith("json"): raw = raw[4:]
            spec = json.loads(raw.strip())
        else:
            raise ValueError(f"Designer returned invalid JSON:\n{raw}")

    if verbose:
        print(f"[Designer] Done.")
        print(f"  - Architecture: {spec.get('architecture')}")
        print(f"  - Tools selected: {spec.get('tools')}")
        print(f"  - System prompt length: {len(spec.get('system_prompt',''))} chars")
        print(f"  - Reasoning: {spec.get('reasoning','')[:100]}...")

    return spec