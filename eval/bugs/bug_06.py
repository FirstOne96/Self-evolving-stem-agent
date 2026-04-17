# Task: reverse a string
def reverse_string(s):
    result = ""
    for i in range(len(s)):  # BUG: should be range(len(s)-1, -1, -1) or just s[::-1]
        result += s[i]
    return result
