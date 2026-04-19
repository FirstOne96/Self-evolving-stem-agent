# eval/ground_truth.py
# 20 bugs total: 01-15 (single-function) + a-e (multi-function/runtime)
# Each has: description, exact_fault (the precise expression that is wrong),
# and keywords for fallback keyword scoring.

GROUND_TRUTH = {
    # ── Single-function bugs (01-15) ────────────────────────────────────
    "bug_01": {
        "description": "Loop starts at index 1 instead of 0, skipping the first element",
        "exact_fault": "range(1, len(nums)) — should be range(0, len(nums)) or range(len(nums))",
        "keywords": ["range(1", "index 1", "skips first", "should start at 0", "off-by-one"]
    },
    "bug_02": {
        "description": "Comparison uses == 1 instead of == 0 to check for even number",
        "exact_fault": "n % 2 == 1 — should be n % 2 == 0",
        "keywords": ["== 1", "should be == 0", "wrong comparison", "returns true for odd"]
    },
    "bug_03": {
        "description": "Mutable default argument — the list is shared across all function calls",
        "exact_fault": "lst=[] in the function signature — should be lst=None with lst = lst or [] inside",
        "keywords": ["mutable default", "default argument", "shared", "persists", "lst=[]"]
    },
    "bug_04": {
        "description": "Returns variable 'a' instead of 'result' — always returns the first argument",
        "exact_fault": "return a — should be return result",
        "keywords": ["return a", "should return result", "wrong variable"]
    },
    "bug_05": {
        "description": "Uses = (assignment) instead of == (comparison) in the if condition",
        "exact_fault": "if len(nums) = 0 — should be if len(nums) == 0",
        "keywords": ["= 0", "== 0", "assignment", "should be ==", "SyntaxError"]
    },
    "bug_06": {
        "description": "Loop iterates forward through the string — doesn't reverse it",
        "exact_fault": "range(len(s)) iterates forward — should be range(len(s)-1, -1, -1) or s[::-1]",
        "keywords": ["forward", "not reversed", "should iterate backward", "wrong direction", "s[::-1]"]
    },
    "bug_07": {
        "description": "Index len(lst) is out of range — last valid index is len(lst)-1",
        "exact_fault": "lst[len(lst)] — should be lst[len(lst)-1] or lst[-1]",
        "keywords": ["len(lst)", "out of range", "len(lst)-1", "IndexError", "lst[-1]"]
    },
    "bug_08": {
        "description": "Missing 'return' keyword in recursive case — returns None instead of the result",
        "exact_fault": "factorial(n - 1) * n — should be return factorial(n - 1) * n",
        "keywords": ["return factorial", "missing return", "returns None", "return keyword"]
    },
    "bug_09": {
        "description": "Condition is inverted — keeps negative numbers instead of positive ones",
        "exact_fault": "if n <= 0 — should be if n > 0",
        "keywords": ["<= 0", "> 0", "inverted", "wrong condition", "keeps negatives"]
    },
    "bug_10": {
        "description": "Dictionary key 'Age' (capital A) does not match actual key 'age' (lowercase)",
        "exact_fault": "person['Age'] — should be person['age']",
        "keywords": ["Age", "age", "lowercase", "capital", "wrong key", "key mismatch"]
    },
    "bug_11": {
        "description": "Loop uses i-1 as index — when i=0, index is -1 which reads the last element first",
        "exact_fault": "transactions[i - 1] — should be transactions[i]",
        "keywords": ["i - 1", "i-1", "index -1", "last element", "when i is 0"]
    },
    "bug_12": {
        "description": "Palindrome index s[len(s) - i] is off by one — should be s[len(s) - i - 1]",
        "exact_fault": "s[len(s) - i] — should be s[len(s) - i - 1]",
        "keywords": ["len(s) - i", "off by one", "should be len(s) - i - 1", "IndexError"]
    },
    "bug_13": {
        "description": "result.append(item) is outside the if block — appends every item including duplicates",
        "exact_fault": "result.append(item) is at the wrong indentation level — should be inside 'if item not in seen'",
        "keywords": ["outside", "indentation", "inside the if", "every item", "always appends"]
    },
    "bug_14": {
        "description": "counts[word] = 1 in the else branch resets the count instead of incrementing",
        "exact_fault": "counts[word] = 1 in the else branch — should be counts[word] += 1",
        "keywords": ["= 1", "should be +=", "resets", "+= 1", "always sets to 1"]
    },
    "bug_15": {
        "description": "low = mid never advances the lower bound — causes infinite loop",
        "exact_fault": "low = mid — should be low = mid + 1",
        "keywords": ["low = mid", "mid + 1", "infinite loop", "never advances", "should be mid + 1"]
    },

    # ── Multi-function / runtime bugs (a-e) ─────────────────────────────
    "bug_a": {
        "description": "DEFAULT_ITEM is a module-level dict mutated every call — all cart items point to the same object",
        "exact_fault": "item = DEFAULT_ITEM reuses the same dict object — should be item = DEFAULT_ITEM.copy() or item = {}",
        "keywords": ["DEFAULT_ITEM", "same dict", "shared", "module-level", "mutated", "same object", ".copy()"]
    },
    "bug_b": {
        "description": "Sliding window loop range misses the last window",
        "exact_fault": "range(1, len(nums) - k) — should be range(1, len(nums) - k + 1)",
        "keywords": ["len(nums) - k", "- k + 1", "last window", "off by one", "+ 1"]
    },
    "bug_c": {
        "description": "Generator from parse_records is exhausted by count_valid — summarise receives nothing",
        "exact_fault": "parsed is a generator consumed by count_valid — summarise should call parse_records(raw_list) again, or parsed should be list(parse_records(raw_list))",
        "keywords": ["generator", "exhausted", "consumed", "restarted", "count_valid", "iterate twice", "list("]
    },
    "bug_d": {
        "description": "Float comparison to 0 fails due to IEEE 754 precision — 0.1+0.1+0.1-0.3 is not exactly 0.0",
        "exact_fault": "self.balance < 0 — should use abs(self.balance) < epsilon or round(self.balance, 10) < 0",
        "keywords": ["float", "epsilon", "0.1", "floating point", "precision", "not exactly zero", "1e-", "abs("]
    },
    "bug_e": {
        "description": "flatten_memo passes depth unchanged — cache keys collide across different sublists",
        "exact_fault": "flatten_memo(item, depth) — should be flatten_memo(item, depth + 1)",
        "keywords": ["depth", "depth+1", "depth + 1", "cache", "collide", "same key", "stale"]
    },
}