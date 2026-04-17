# ground_truth.py
# For each bug file, we store:
#   - "description": the actual bug in plain English
#   - "keywords": words the agent's answer MUST contain to be counted correct
#     (we check if any keyword appears in the agent's response, case-insensitive)

GROUND_TRUTH = {
    "bug_01": {
        "description": "Loop starts at index 1 instead of 0, skipping the first element",
        "keywords": ["range(1", "index 1", "starts at 1", "skips first", "should start at 0", "off-by-one"]
    },
    "bug_02": {
        "description": "Comparison uses == 1 instead of == 0 to check for even number",
        "keywords": ["== 1", "should be == 0", "== 0", "wrong comparison", "returns true for odd"]
    },
    "bug_03": {
        "description": "Mutable default argument — the list is shared across all function calls",
        "keywords": ["mutable default", "default argument", "shared", "persists", "mutable"]
    },
    "bug_04": {
        "description": "Returns variable 'a' instead of 'result' — always returns the first argument",
        "keywords": ["return a", "should return result", "returns a", "wrong variable", "return result"]
    },
    "bug_05": {
        "description": "Uses = (assignment) instead of == (comparison) in the if condition",
        "keywords": ["= 0", "== 0", "assignment", "should be ==", "syntax error", "SyntaxError"]
    },
    "bug_06": {
        "description": "Loop iterates forward through the string instead of backward — doesn't actually reverse",
        "keywords": ["forward", "not reversed", "should iterate backward", "range(len(s)-1", "wrong direction", "s[::-1]"]
    },
    "bug_07": {
        "description": "Index len(lst) is out of range — last valid index is len(lst)-1",
        "keywords": ["len(lst)", "out of range", "len(lst)-1", "IndexError", "last index", "lst[-1]"]
    },
    "bug_08": {
        "description": "Missing 'return' keyword in the recursive case — returns None instead of the result",
        "keywords": ["return factorial", "missing return", "no return", "returns None", "return keyword"]
    },
    "bug_09": {
        "description": "Condition is inverted — <= 0 keeps negatives instead of > 0 keeping positives",
        "keywords": ["<= 0", "> 0", "inverted", "wrong condition", "keeps negatives", "should be > 0"]
    },
    "bug_10": {
        "description": "Dictionary key is 'Age' (capital A) but actual key is 'age' (lowercase)",
        "keywords": ["Age", "age", "lowercase", "capital", "case", "wrong key", "key mismatch"]
    },
}
