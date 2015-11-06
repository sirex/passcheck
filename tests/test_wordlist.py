import os
import tempfile
import pytest

from passcheck import wordlist


def test_load(request):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(
            b'one\n'
            b'two\n'
            b'three\n'
        )
    request.addfinalizer(lambda: os.unlink(f.name))
    assert wordlist.load(f.name) == {b'one': 1, b'two': 2, b'three': 3}


def test_load_missing(request):
    with tempfile.NamedTemporaryFile() as f:
        pass
    assert wordlist.load(f.name) == {}


def test_load_required_missing(request):
    with tempfile.NamedTemporaryFile() as f:
        pass
    with pytest.raises(FileNotFoundError):
        wordlist.load(f.name, required=True)
