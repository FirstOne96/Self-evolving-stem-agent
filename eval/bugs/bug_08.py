# Task: compute factorial recursively
def factorial(n):
    if n == 0:
        return 1
    else:
        factorial(n - 1) * n  # BUG: missing return keyword
