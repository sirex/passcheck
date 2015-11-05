from passcheck.generators import substrings


def test_substrings_empty():
    assert list(substrings('')) == []


def test_substrings_single():
    assert list(substrings('a')) == ['a']


def test_substrings():
    assert list(substrings('abc')) == [
        'a', 'ab', 'abc',
        'b', 'bc',
        'c',
    ]


# def test_combinations():
#     s = 'abc'
#     k = len(s)
#     tokens = []
#     mapping = collections.defaultdict(list)
#     items = collections.defaultdict(list)
#     for i in range(k):
#         for j in range(i, k):
#             tokens.append((i, j+1, s[i:j+1]))
#             mapping[i].append((j+1, s[i:j+1]))
