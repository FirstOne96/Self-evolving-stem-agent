# agents/base_agent.py
from openai import OpenAI
from config import OPENAI_API_KEY, AGENT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

GENERIC_SYSTEM_PROMPT = """You are a helpful code reviewer.
Look at the code and describe any bugs you find."""

USER_MESSAGE = """This code contains exactly one bug. 
Identify it: describe the specific line or expression that is wrong, 
why it produces incorrect behavior, and what it should be instead.
Do not generate test cases. Do not suggest refactors. 
Just describe the one bug that is already present.

Code:
{code}"""


class GenericAgent:
    def __init__(self):
        self.system_prompt = GENERIC_SYSTEM_PROMPT
        self.name = "GenericAgent"

    def run(self, code: str) -> str:
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": USER_MESSAGE.format(code=code)},
            ],
            temperature=0.2,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()


class SpecializedAgent:
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
                {"role": "user",   "content": USER_MESSAGE.format(code=code)},
            ],
            temperature=0.2,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()