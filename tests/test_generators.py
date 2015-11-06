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
