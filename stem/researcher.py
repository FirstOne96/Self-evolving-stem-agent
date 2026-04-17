# stem/researcher.py
#
# The Researcher is Phase 1 of the stem loop.
# It takes a domain name and asks GPT-4o to produce a structured
# "domain map" — a synthesis of how that class of problems is typically solved.

import json
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


RESEARCHER_SYSTEM_PROMPT = """You are an expert AI systems researcher.
Your job is to analyze a problem domain and produce a structured map of 
how AI agents are typically built to solve it.

You must respond with valid JSON only. No markdown, no explanation outside the JSON.

Your JSON must follow this exact structure:
{
  "domain": "<domain name>",
  "summary": "<2-3 sentence overview of how this domain is typically approached>",
  "tools": [
    {"name": "<tool name>", "purpose": "<what it does>", "importance": "high|medium|low"}
  ],
  "architectures": [
    {"name": "<architecture name>", "description": "<how it works>", "best_for": "<when to use it>"}
  ],
  "prompt_patterns": [
    {"name": "<pattern name>", "template": "<the actual prompt structure>", "why_it_works": "<explanation>"}
  ],
  "failure_modes": [
    {"mode": "<failure name>", "description": "<what goes wrong>", "mitigation": "<how to avoid it>"}
  ],
  "recommended_approach": {
    "architecture": "<which architecture to use and why>",
    "key_tools": ["<tool1>", "<tool2>"],
    "system_prompt_focus": "<what the system prompt should emphasize>",
    "evaluation_strategy": "<how to measure success>"
  }
}"""


RESEARCHER_USER_PROMPT = """Research the following AI agent domain and produce a domain map:

Domain: {domain}

Focus specifically on:
1. What tools are most effective for this domain
2. What agent architectures work best (single agent, chain-of-thought, critic loop, etc.)
3. What prompt patterns produce reliable results
4. What failure modes are most common and how to avoid them
5. What a recommended first implementation should look like

Be concrete and specific. Your output will be used to automatically configure an AI agent."""


def run_researcher(domain: str, verbose: bool = True) -> dict:
    """
    Research a domain and return a structured domain map.

    Args:
        domain:  The problem domain (e.g. "QA / Bug Finding")
        verbose: Whether to print progress

    Returns:
        A dict containing the domain map
    """
    if verbose:
        print(f"\n[Researcher] Researching domain: '{domain}'...")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": RESEARCHER_SYSTEM_PROMPT},
            {"role": "user",   "content": RESEARCHER_USER_PROMPT.format(domain=domain)},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()

    # Parse JSON — strip accidental markdown fences if present
    try:
        domain_map = json.loads(raw)
    except json.JSONDecodeError as e:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            domain_map = json.loads(raw.strip())
        else:
            raise ValueError(f"Researcher returned invalid JSON: {e}\n\nRaw:\n{raw}")

    if verbose:
        print(f"[Researcher] Done. Found:")
        print(f"  - {len(domain_map.get('tools', []))} tools")
        print(f"  - {len(domain_map.get('architectures', []))} architectures")
        print(f"  - {len(domain_map.get('prompt_patterns', []))} prompt patterns")
        print(f"  - {len(domain_map.get('failure_modes', []))} failure modes")
        print(f"  - Recommended arch: {domain_map.get('recommended_approach', {}).get('architecture', 'N/A')[:80]}")

    return domain_map