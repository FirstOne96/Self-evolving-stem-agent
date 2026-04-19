# Reads records from a data source, filters valid ones, then counts and summarises them.
# parse_records returns a generator of dicts.
# count_valid counts records where "active" is True.
# summarise returns a list of names from valid records.
# The caller runs both count_valid and summarise on the same parsed output.

def parse_records(raw_list):
    for entry in raw_list:
        if isinstance(entry, dict):
            yield entry

def count_valid(records):
    return sum(1 for r in records if r.get("active"))

def summarise(records):
    return [r["name"] for r in records if r.get("active")]

def process(raw_list):
    parsed = parse_records(raw_list)   # BUG: generator is exhausted after count_valid
    count  = count_valid(parsed)       # consumes the generator
    names  = summarise(parsed)         # gets nothing — generator already done
    return count, names
