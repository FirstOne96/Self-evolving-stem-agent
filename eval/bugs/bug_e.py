# A recursive function that flattens a nested list of arbitrary depth.
# flatten([1, [2, [3, 4]], 5]) should return [1, 2, 3, 4, 5]

def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

# The function above is correct. The bug is in this memoized version:

_cache = {}

def flatten_memo(lst, depth=0):
    key = (id(lst), depth)
    if key in _cache:
        return _cache[key]
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_memo(item, depth))  # BUG: should pass depth+1
        else:                                           # without incrementing depth,
            result.append(item)                        # cache keys collide across calls
    _cache[key] = result
    return result
