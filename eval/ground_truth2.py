# eval/ground_truth.py
#
# Ground truth for the realistic benchmark (bugs A-E).
# These bugs require understanding multi-function interactions,
# not just pattern-matching to known Python pitfalls.

GROUND_TRUTH = {
    "bug_a": {
        "description": "DEFAULT_ITEM is a module-level dict that gets mutated every call — all cart items end up pointing to the same object, so the cart always reflects the last item added",
        "keywords": ["DEFAULT_ITEM", "same dict", "shared", "module-level", "mutated", "same object", "reuses", "mutable default"]
    },
    "bug_b": {
        "description": "Loop range is len(nums) - k instead of len(nums) - k + 1 — the last sliding window is never evaluated",
        "keywords": ["len(nums) - k", "- k + 1", "last window", "off by one", "misses last", "range", "+ 1"]
    },
    "bug_c": {
        "description": "parse_records returns a generator that is fully consumed by count_valid — when summarise runs on the same generator it receives nothing because generators cannot be restarted",
        "keywords": ["generator", "exhausted", "consumed", "restarted", "count_valid", "already", "once", "iterate twice"]
    },
    "bug_d": {
        "description": "Floating point arithmetic means 0.1 + 0.1 + 0.1 - 0.3 is not exactly 0.0 — the balance comparison should use an epsilon or round() to avoid false overdraft detection",
        "keywords": ["float", "epsilon", "0.1", "rounding", "floating point", "precision", "not exactly zero", "tiny", "1e-"]
    },
    "bug_e": {
        "description": "flatten_memo passes depth unchanged into recursive calls — cache keys collide because different sublists at different nesting levels share the same (id, depth) key, returning stale cached results",
        "keywords": ["depth", "depth+1", "cache", "collide", "same key", "id(lst)", "stale", "memoiz"]
    },
}
