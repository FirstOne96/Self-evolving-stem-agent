# Task: return the sum of all elements in a list
def sum_list(nums):
    total = 0
    for i in range(1, len(nums)):  # BUG: should start at 0, skips first element
        total += nums[i]
    return total
