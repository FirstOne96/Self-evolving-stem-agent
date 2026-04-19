# Task: count how many times each word appears in a list and return a dictionary
def word_count(words):
    counts = {}
    for word in words:
        if word not in counts:
            counts[word] = 1
        else:
            counts[word] = 1  # BUG: should be counts[word] += 1, resets to 1 instead of incrementing
    return counts
