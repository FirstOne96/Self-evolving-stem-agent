# Task: return the maximum of two numbers
def max_of_two(a, b):
    if a > b:
        result = a
    else:
        result = b
    return a  # BUG: should return result (or b in else branch logic)
