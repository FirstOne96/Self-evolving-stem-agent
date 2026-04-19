# stem/researcher.py
#
# Phase 1 of the stem loop.
# Takes a domain name and asks GPT-4o to produce a structured "domain map" —
# basically a summary of how agents for that domain are typically built.
# The map covers tools, architectures, prompt patterns, and failure modes.
# This runs once at the start and the result gets passed to the Designer.

import json
from openai import OpenAI
from config import OPENAI_API_KEY, JUDGE_MODEL

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


def run_researcher(domain, verbose=True):
    """
    Ask GPT-4o to research the domain and return a domain map as a dict.

    The domain map is used by the Designer to decide what kind of agent to build.
    It includes tools, architectures, prompt patterns, and known failure modes.
    If the model wraps its response in markdown fences we strip those out.
    """
    if verbose:
        print(f"\n[Researcher] Researching domain: '{domain}'...")

    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": RESEARCHER_SYSTEM_PROMPT},
            {"role": "user",   "content": RESEARCHER_USER_PROMPT.format(domain=domain)},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()

    try:
        domain_map = json.loads(raw)
    except json.JSONDecodeError as e:
        # sometimes the model wraps json in ```json ... ``` even when told not to
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