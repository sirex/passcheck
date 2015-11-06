from passcheck.formatting import format_number, format_seconds


def test_format_number():
    assert format_number(10**6) == '1,000,000'
    assert format_number(10**11) == '1.000000e+11'


def test_format_seconds():
    assert format_seconds(0.5) == '0.500000 seconds'
    assert format_seconds(1) == '1 second'
    assert format_seconds(42) == '42 seconds'
    assert format_seconds(60 * 1) == '1 minute'
    assert format_seconds(60 * 42) == '42 minutes'
    assert format_seconds(60 * 60 * 1) == '1 hour'
    assert format_seconds(60 * 60 * 8) == '8 hours'
    assert format_seconds(60 * 60 * 24 * 1) == '1 day'
    assert format_seconds(60 * 60 * 24 * 4) == '4 days'
    assert format_seconds(60 * 60 * 24 * 7 * 1) == '1 week'
    assert format_seconds(60 * 60 * 24 * 7 * 3) == '3 weeks'
    assert format_seconds(60 * 60 * 24 * 30 * 1) == '1 month'
    assert format_seconds(60 * 60 * 24 * 30 * 3) == '3 months'
    assert format_seconds(60 * 60 * 24 * 365 * 1) == '1 year'
    assert format_seconds(60 * 60 * 24 * 365 * 10) == '10 years'
    assert format_seconds(60 * 60 * 24 * 365 * 100) == '100 years'
