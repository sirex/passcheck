from itertools import combinations


def substrings(s):
    """Split iterable s into all possible tokens preserving order."""
    for i, j in combinations(range(len(s) + 1), 2):
        yield s[i:j]
