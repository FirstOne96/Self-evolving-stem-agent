# Task: given a sorted list and a target, return the index of target using binary search
# return -1 if not found
def binary_search(lst, target):
    low  = 0
    high = len(lst) - 1
    while low <= high:
        mid = (low + high) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            low = mid      # BUG: should be mid + 1 — never advances past mid, causes infinite loop
        else:
            high = mid - 1
    return -1
