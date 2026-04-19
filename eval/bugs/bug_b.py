# Computes the maximum sum of any contiguous subarray of length k.
# Example: max_window_sum([1, 3, 2, 6, -1, 4], k=3) should return 11 (2+6+(-1)+4 = no, window [3,2,6]=11)

def max_window_sum(nums, k):
    if len(nums) < k:
        return 0
    window = sum(nums[:k])
    best = window
    for i in range(1, len(nums) - k):  # BUG: should be len(nums) - k + 1, misses last window
        window = window - nums[i - 1] + nums[i + k - 1]
        best = max(best, window)
    return best
