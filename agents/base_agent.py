# agents/base_agent.py
from openai import OpenAI
from config import OPENAI_API_KEY, AGENT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

# Generic prompt — intentionally vague, like a real "first try" prompt.
# Asks for bugs but doesn't force step-by-step tracing or precision.
GENERIC_SYSTEM_PROMPT = """You are a code reviewer. 
Read the code and describe any bugs you find."""

GENERIC_USER = """Find the bug in this code and briefly describe what is wrong.

{code}"""

# Specialized prompt template — filled in by the Designer from the domain map.
# The Designer is expected to produce something that forces:
#   (1) line-by-line execution tracing
#   (2) naming the exact wrong expression
#   (3) explaining why it fails
SPECIALIZED_USER = """This code contains exactly one bug.
Identify it precisely: name the exact expression or line that is wrong,
explain why it produces incorrect behavior, and state what it should be.

{code}"""


class GenericAgent:
    """
    Baseline — generic system prompt, vague user message.
    Represents what you get before any specialization.
    Will often score 1/2 (correct area, imprecise explanation).
    """
    def __init__(self):
        self.system_prompt = GENERIC_SYSTEM_PROMPT
        self.name = "GenericAgent"

    def run(self, code: str) -> str:
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
    Specialized — system prompt written by the Designer, precise user message.
    The Designer's system prompt forces step-by-step tracing.
    Will score 2/2 when the trace leads to the exact faulty expression.
    """
    def __init__(self, spec: dict):
        self.system_prompt = spec["system_prompt"]
        self.strategy      = spec.get("strategy", "")
        self.architecture  = spec.get("architecture", "")
        self.tools         = spec.get("tools", [])
        self.name          = "SpecializedAgent"

    def run(self, code: str) -> str:
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