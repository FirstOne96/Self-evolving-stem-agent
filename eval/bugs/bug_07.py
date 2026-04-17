# Task: return the last element of a list
def last_element(lst):
    return lst[len(lst)]  # BUG: index out of range, should be len(lst)-1 or lst[-1]
