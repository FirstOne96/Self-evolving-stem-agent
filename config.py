# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # reads your .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

# How many evolution attempts before we give up
MAX_EVOLUTION_ROUNDS = 3

# Score threshold — if the agent hits this, it stops evolving and starts executing
SUCCESS_THRESHOLD = 0.6  # 60% of bugs found correctly