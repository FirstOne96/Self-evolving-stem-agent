# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# The model the AGENTS use (generic + specialized)
# gpt-4o-mini is cheaper and weaker at pattern recognition —
# this creates a real gap that specialization can close
AGENT_MODEL = "gpt-4o-mini"

# The model used as judge in the strict benchmark
# Needs to be strong enough to evaluate answers correctly
JUDGE_MODEL = "gpt-4o"

# Keep backward compat — MODEL still works for other uses
MODEL = AGENT_MODEL

MAX_EVOLUTION_ROUNDS = 3
SUCCESS_THRESHOLD = 0.6