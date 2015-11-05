from itertools import combinations


def substrings(s):
    """Split iterable s into all possible tokens preserving order."""
    for i, j in combinations(range(len(s) + 1), 2):
        yield s[i:j]


def compositions(items, i=0):
    for j, item in reversed(items[i]):
        if j in items:
            for row in compositions(items, j):
                yield (item,) + row
        else:
            yield (item,)
