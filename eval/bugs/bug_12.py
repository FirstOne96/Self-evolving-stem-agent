# Task: return True if the given string is a palindrome (reads same forwards and backwards)
def is_palindrome(s):
    for i in range(len(s) // 2):
        if s[i] != s[len(s) - i]:  # BUG: should be s[len(s) - i - 1], causes IndexError or wrong check
            return False
    return True
