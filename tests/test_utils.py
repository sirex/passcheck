from passcheck.utils import is_binary


def test_is_binary():
    assert is_binary(b'\0') is True
    assert is_binary(b'a') is False
