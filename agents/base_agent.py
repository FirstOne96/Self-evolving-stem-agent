# agents/base_agent.py
#
# Two agent classes: GenericAgent and SpecializedAgent.
# GenericAgent is the baseline — vague prompt, no special instructions.
# SpecializedAgent gets its system prompt from the Designer.
#
# Both use the same underlying model (gpt-4o-mini) so the only
# difference is the system prompt the Designer produced.

from openai import OpenAI
from config import OPENAI_API_KEY, AGENT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

# deliberately vague — represents what you'd write on a first attempt
GENERIC_SYSTEM_PROMPT = """You are a code reviewer. 
Read the code and describe any bugs you find."""

# the generic user message is also intentionally unspecific
# it asks for bugs but doesn't force any particular reasoning style
GENERIC_USER = """Find the bug in this code and briefly describe what is wrong.

{code}"""

# the specialized user message tells the agent exactly what format is expected.
# the system prompt (from the Designer) handles HOW to reason — this just
# tells it what the output should look like.
SPECIALIZED_USER = """This code contains exactly one bug.
Identify it precisely: name the exact expression or line that is wrong,
explain why it produces incorrect behavior, and state what it should be.

{code}"""


class GenericAgent:
    """
    The baseline agent — no specialization at all.

    Uses a vague system prompt and a vague user message.
    In practice this scores well on correctness (finds the bug area)
    but badly on precision (doesn't name the exact expression).
    That's the gap the stem loop tries to close.
    """

    def __init__(self):
        self.system_prompt = GENERIC_SYSTEM_PROMPT
        self.name = "GenericAgent"

    def run(self, code):
        """Send the code to gpt-4o-mini with no special instructions and return the answer."""
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": GENERIC_USER.format(code=code)},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()


class SpecializedAgent:
    """
    The evolved agent — system prompt was written by the Designer based on domain research.

    Gets the same user message as the generic agent (asking for exact expression),
    but the system prompt tells it HOW to reason: trace line by line, name exact
    expressions, explain why they fail. That combination is what closes the precision gap.
    """

    def __init__(self, spec):
        # spec comes from run_designer() — it's a dict with system_prompt, architecture, etc.
        self.system_prompt = spec["system_prompt"]
        self.strategy      = spec.get("strategy", "")
        self.architecture  = spec.get("architecture", "")
        self.tools         = spec.get("tools", [])
        self.name          = "SpecializedAgent"

    def run(self, code):
        """Send the code using the Designer's system prompt and return the answer."""
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": SPECIALIZED_USER.format(code=code)},
            ],
            temperature=0.2,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()