![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black.svg)

# 🧬 Stem Agent

A self-specializing AI agent for QA / Bug Finding.

Given a domain name, the system researches how agents in that domain are typically built, designs its own system prompt based on that research, runs against a benchmark, and evolves until it's good enough — or runs out of rounds.

---

## 🛠️ Setup

**Requirements**

- Python 3.10+
- An OpenAI API key

**Install dependencies**

```bash
pip install requirements.txt
```

**Add your API key**

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-key-here
```

**Run**

```bash
python main.py
```

Results are printed to the terminal and saved to `logs/evolution.json`.

---

## 🧱 Project structure

```
stem-agent/
├── main.py               # entry point — runs the full evolution loop
├── config.py             # API keys, model names, thresholds
│
├── stem/
│   ├── researcher.py     # phase 1 — researches the domain
│   ├── designer.py       # phase 2 — writes its own system prompt
│   ├── builder.py        # phase 3 — runs both agents on the benchmark
│   └── evaluator.py      # phase 4 — stop or loop decision
│
├── agents/
│   └── base_agent.py     # GenericAgent (baseline) and SpecializedAgent
│
└── eval/
    ├── benchmark.py      # LLM-as-judge scorer (2 dimensions per bug)
    ├── ground_truth.py   # answer key for all 20 bugs
    └── bugs/             # 20 Python files each with one bug
```

---

## 🧠 How it works

The system runs a four-phase loop, inspired by how a stem cell specializes — it starts generic and grows into something specific by reading signals from its environment.

### Phase 1 — Researcher
Takes the domain name (`"QA / Bug Finding"`) and asks GPT-4o to produce a structured domain map: what tools are used, what architectures work, what prompt patterns are effective, and what failure modes are common. This runs once at the start.

### Phase 2 — Designer
Reads the domain map and writes a complete agent specification — a system prompt, architecture choice, and reasoning strategy — without any human input. On subsequent rounds it also receives the list of bugs that were answered poorly, and adjusts specifically for those.

### Phase 3 — Builder
Instantiates two agents — the generic baseline (vague prompt, no special instructions) and the specialized agent (Designer's system prompt) — and runs both against the benchmark. This gives a before/after comparison in the same round.

### Phase 4 — Evaluator
Checks the specialized agent's score against the threshold (60%). If it passes, evolution stops. If not, the evaluator collects which bugs were wrong or vague and passes that back to the Designer for another round. Maximum three rounds.

```
domain name
    │
    ▼
[Researcher] → domain map
    │
    ▼
[Designer] ←─────────────── failure feedback (on retry rounds)
    │
    ▼
[Builder] → runs generic agent + specialized agent on benchmark
    │
    ▼
[Evaluator] → STOP (threshold met) or LOOP (feed failures back)
    │
    ▼
logs/evolution.json
```

---

## 🧩 Benchmark

The benchmark is 20 Python functions, each with exactly one bug. Bugs are split into two tiers:

**Tier 1 — single-function bugs (01–15)**
Classic Python pitfalls: off-by-one in `range()`, wrong comparison operator, mutable default argument, missing `return`, inverted condition, wrong dictionary key casing. Also includes harder trace-required variants: negative index from `i-1`, palindrome index error, indentation bug, counter reset instead of increment, infinite loop in binary search.

**Tier 2 — multi-function / runtime bugs (a–e)**
Bugs that require understanding how functions interact or knowing Python runtime behavior:

| Bug | What it is |
|-----|-----------|
| `bug_a` | Module-level mutable dict shared across all `add_item` calls |
| `bug_b` | Sliding window `range()` misses the last window |
| `bug_c` | Generator exhausted by first consumer — second gets nothing |
| `bug_d` | `0.1 + 0.1 + 0.1 - 0.3` is not exactly `0.0` in IEEE 754 |
| `bug_e` | Cache key collision from non-incrementing recursion depth |

### Scoring

Every answer is scored on two axes by GPT-4o acting as judge:

| Dimension | Score 1 | Score 0 |
|-----------|---------|---------|
| **Correctness** | Identified the right bug | Wrong or fundamentally misunderstood |
| **Precision** | Named the exact expression or line (e.g. `range(1, len(nums))`) | Described the general area vaguely |

Max score: 40 points (20 bugs × 2). Final score is `total / 40`.

The two-axis design is the key decision. A generic prompt reliably scores 1/2 — it finds the bug area but describes it vaguely. A specialized prompt that forces step-by-step tracing scores 2/2 by driving the model to name exact expressions. The gap between those two numbers is what the stem loop is trying to close.

---

## 📊 Results

| Agent | Score | Full (2/2) | Vague (1/2) | Wrong (0/2) |
|-------|-------|-----------|------------|------------|
| Generic gpt-4o-mini (baseline) | 35/40 = **88%** | 15 | 5 | 0 |
| Specialized gpt-4o-mini | 40/40 = **100%** | 20 | 0 | 0 |
| **Improvement** | **+12%** | +5 bugs | −5 bugs | — |

The loop ran one round and stopped. Every point of improvement came from the precision dimension — all 20 bugs were found by both agents, but 5 were described vaguely by the generic agent and precisely by the specialized one. The Designer produced a trace-focused system prompt that closed that gap entirely in one round.

---

## ⚙️ Configuration

All settings are in `config.py`:

```python
AGENT_MODEL = "gpt-4o-mini"   # model used for the agents under test
JUDGE_MODEL = "gpt-4o"        # model used for research, design, and judging

MAX_EVOLUTION_ROUNDS = 3       # stop after this many rounds regardless
SUCCESS_THRESHOLD    = 0.6     # stop early if specialized agent hits this score
```

The model split is intentional. `gpt-4o-mini` has a genuine precision gap on vague prompts — it identifies bugs correctly but tends to describe them imprecisely without explicit tracing instructions. `gpt-4o` is used for the judge and designer because those roles need stronger reasoning.

---

## 🗂️ Logs

After each run, `logs/` contains:

- `evolution.json` — full record of every round: system prompt used, scores, which bugs failed, why the loop stopped
- `domain_map.json` — the domain research the Researcher produced
- `agent_spec_round{N}.json` — the agent specification the Designer produced each round

---

## 📞 Contact:
Andrii Kozlov - andrijkozlov96@gmail.com  | https://t.me/AndrewKozz | https://www.linkedin.com/in/andrii-kozlov96<br>
