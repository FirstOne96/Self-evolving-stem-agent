# Task: append an item to a list and return it
def append_item(item, lst=[]):  # BUG: mutable default argument, shared across calls
    lst.append(item)
    return lst
