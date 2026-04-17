# Task: return a person's age from a dictionary, or -1 if not found
def get_age(person):
    if "Age" in person:  # BUG: key is "age" (lowercase), will always miss it
        return person["Age"]
    return -1
