import os
import string
import tempfile

from math import ceil
from unittest.mock import patch, Mock

from passcheck.passcheck import PassCheck, Value
from passcheck import patterns as pt


digits = set(string.digits.encode())
lowercase = set(string.ascii_lowercase.encode())
uppercase = set(string.ascii_uppercase.encode())
letters = set(string.ascii_letters.encode())
punctuation = set(string.punctuation.encode())
allbytes = set(range(256))


def test_pattern_str_representation():
    pattern = pt.Pattern('title')
    assert str(pattern) == 'title'


def test_same_chars():
    passcheck = PassCheck([pt.SingleBytePattern('', lowercase)])
    result = passcheck.get_result('rrrrr')
    assert result.combinations == 130
    assert ceil(result.entropy) == 8


def test_digits():
    passcheck = PassCheck([pt.MultipleBytesPattern('', digits)])
    result = passcheck.get_result('1234')
    assert result.combinations == 11110
    assert ceil(result.entropy) == 14


def test_lowercase():
    passcheck = PassCheck([pt.MultipleBytesPattern('', lowercase)])
    result = passcheck.get_result('abcde')
    assert result.combinations == 12356630
    assert ceil(result.entropy) == 24


def test_letters():
    passcheck = PassCheck([pt.MultipleBytesPattern('', letters)])
    result = passcheck.get_result('Abcde')
    assert result.combinations == 387659012
    assert ceil(result.entropy) == 29


def test_allbytes():
    passcheck = PassCheck([pt.MultipleBytesPattern('', allbytes)])
    result = passcheck.get_result(b'\0\1\2\4\5')
    assert result.combinations == 1103823438080
    assert ceil(result.entropy) == 41


def test_dict():
    passcheck = PassCheck([pt.DictPattern('', [b'pass', b'passwd'])])
    result = passcheck.get_result('pass')
    assert result.combinations == 2
    assert ceil(result.entropy) == 1


def test_title_case_dict():
    passcheck = PassCheck([pt.TitleCaseDictPattern('', [b'pass', b'passwd'])])
    result = passcheck.get_result('Pass')
    assert result.combinations == 4
    assert ceil(result.entropy) == 2


def test_case_insensitive_dict():
    passcheck = PassCheck([pt.CaseInsensitiveDictPattern('', [b'pass', b'passwd'])])
    result = passcheck.get_result('PasS')
    assert result.combinations == 2**len('pass') + 2**len('passwd')
    assert ceil(result.entropy) == 7


def test_case_insensitive_dict_ranked():
    passcheck = PassCheck([pt.CaseInsensitiveDictPattern('', [b'pass', b'passwd'], ranked=True)])
    result = passcheck.get_result('PasS')
    assert result.combinations == 2**len('pass')
    assert ceil(result.entropy) == 4


def test_single_byte_check():
    assert pt.TitleCaseDictPattern('', [b'a']).matches(Value(b'a')) is False


def test_hunspell_absent_not_required():
    with patch.object(pt.HunspellPattern, 'import_hunspell', return_value=None):
        assert pt.HunspellPattern('', 'dpath', 'apath', required=False).word_count == 0


def test_hunspell_installed_required(request):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b'42\n')
    request.addfinalizer(lambda: os.unlink(f.name))

    hunspell = Mock()
    hunspell.HunSpell.return_value.get_dic_encoding = Mock(return_value='utf-8')

    with patch.object(pt.HunspellPattern, 'import_hunspell', return_value=hunspell):
        assert pt.HunspellPattern('', f.name, 'apath', required=True).word_count == 42
