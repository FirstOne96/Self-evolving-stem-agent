# Task: return only the positive numbers from a list
def filter_positives(nums):
    result = []
    for n in nums:
        if n <= 0:  # BUG: should be n > 0
            result.append(n)
    return result
