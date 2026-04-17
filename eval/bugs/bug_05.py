# Task: return the average of a list of numbers, return 0 if empty
def average(nums):
    if len(nums) = 0:  # BUG: should be == not = (assignment in condition)
        return 0
    return sum(nums) / len(nums)
