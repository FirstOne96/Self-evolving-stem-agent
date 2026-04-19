# Task: remove all duplicate values from a list, preserving original order
def remove_duplicates(lst):
    seen = []
    result = []
    for item in lst:
        if item not in seen:
            seen.append(item)
        result.append(item)  # BUG: should be inside the if block — adds every item including duplicates
    return result
