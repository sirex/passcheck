from passcheck.passcheck import get_default_passcheck


def strorbytes(s):
    if isinstance(s, bytes):
        try:
            return s.decode()
        except UnicodeDecodeError:
            return s
    else:
        return s


def check(value, debug=False):
    passcheck = get_default_passcheck(debug=debug)
    results = passcheck.check(value)
    return [strorbytes(r.value.bytes) for r in results]


def test_1():
    assert check('123aaa') == ['123', 'aaa']


def test_2():
    assert check('slaptažodis') == ['slaptažodis']


def test_3():
    assert check('slaptažodis3') == ['slaptažodis', '3']


def test_4():
    assert check('correct&horsebatterystaple') == ['correct', '&', 'horse', 'battery', 'staple']


def test_5():
    assert check(b'\x19\xa8\x1d\xc4\xa3') == [b'\x19\xa8\x1d\xc4\xa3']
