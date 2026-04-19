# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# agents run on the cheaper/weaker model — this creates a real gap
# that specialization can close (gpt-4o-mini misses precision on vague prompts)
AGENT_MODEL = "gpt-4o-mini"

# judge/researcher/designer use the stronger model for quality output
JUDGE_MODEL = "gpt-4o"

MAX_EVOLUTION_ROUNDS = 3
SUCCESS_THRESHOLD = 0.6