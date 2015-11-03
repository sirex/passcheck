import os
import os.path
import argparse
import math
import random
import string
import getpass
import base64


class Value(object):

    def __init__(self, value: bytes):
        self.bytes = value
        self.unique_bytes = set(value)
        self.unique_bytes_count = len(self.unique_bytes)


class MultipleBytesPattern(object):

    def __init__(self, superset: set):
        self.superset = superset

    def matches(self, value):
        return value.unique_bytes <= self.superset

    def combinations(self, value):
        k = len(self.superset)
        n = len(value.bytes)
        return sum(k**i for i in range(1, n + 1))


class SingleBytePattern(MultipleBytesPattern):

    def matches(self, value):
        return value.unique_bytes_count == 1 and super().matches(value)

    def combinations(self, value):
        k = len(self.superset)
        n = len(value.bytes)
        return k * n


def load_words(path, required=False):
    if required or os.path.exists(path):
        with open(path) as f:
            return {w.strip().lower().encode(): i for i, w in enumerate(f, 1)}
    else:
        return {}


class DictPattern(object):

    def __init__(self, words, ranked=False):
        self.words = words
        self.ranked = ranked

    def matches(self, value):
        return value.bytes in self.words

    def combinations(self, value):
        return self.words[value.bytes] if self.ranked else len(self.words)


class TitleCaseDictPattern(DictPattern):

    def matches(self, value):
        v = value.bytes
        v = v[:1].lower() + v[1:]
        return v in self.words

    def combinations(self, value):
        return super().combinations(value) * 2


class CaseInsensitiveDictPattern(DictPattern):

    def matches(self, value):
        return value.bytes.lower() in self.words

    def combinations(self, value):
        c = 0
        for w in self.words:
            c += 2**len(w)
            if self.ranked and w == value.bytes.lower():
                return c
        return c


class Result(object):

    def __init__(self, pattern, value):
        self.combinations = pattern.combinations(value)
        self.entropy = math.log2(self.combinations)


class PassCheck(object):

    def __init__(self, patterns):
        self.patterns = patterns

    def check(self, value):
        value = Value(value.encode()) if isinstance(value, str) else Value(value)
        for pattern in self.patterns:
            if pattern.matches(value):
                return Result(pattern, value)


def format_number(number):
    if number > 1e10:
        return '{:e}'.format(number)
    else:
        return '{:,}'.format(number)


def format_seconds(seconds):
    units = [
        (31536000, 'years'),
        (2592000, 'months'),
        (604800, 'weeks'),
        (86400, 'days'),
        (3600, 'hours'),
        (3600, 'minutes'),
    ]

    for s, unit in units:
        if seconds >= s:
            x = int(seconds // s)
            return '{} {}'.format(format_number(x), unit)

    if seconds > 1:
        return '%d seconds' % seconds
    else:
        return '%f seconds' % seconds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('password', nargs='?')
    parser.add_argument('-p', dest='askpass', action='store_true')

    args = parser.parse_args()

    if args.askpass:
        password = getpass.getpass()
    elif args.password:
        password = args.password
    else:
        password = base64.b85encode(os.urandom(random.randint(8, 32))).decode()
        print('Password: %s' % password)

    digits = set(string.digits.encode())
    lowercase = set(string.ascii_lowercase.encode())
    uppercase = set(string.ascii_uppercase.encode())
    letters = set(string.ascii_letters.encode())
    punctuation = set(string.punctuation.encode())
    allbytes = set(range(256))

    cracklib_words = load_words('/usr/share/dict/cracklib-small', required=False)
    unix_words = load_words('/usr/share/dict/words', required=False)

    passcheck = PassCheck([
        DictPattern(cracklib_words),
        TitleCaseDictPattern(cracklib_words),
        CaseInsensitiveDictPattern(cracklib_words),

        DictPattern(unix_words),
        TitleCaseDictPattern(unix_words),
        CaseInsensitiveDictPattern(unix_words),

        SingleBytePattern(digits),
        SingleBytePattern(lowercase),
        SingleBytePattern(uppercase),
        SingleBytePattern(letters),
        SingleBytePattern(letters | digits),
        SingleBytePattern(letters | punctuation),
        SingleBytePattern(letters | digits | punctuation),
        SingleBytePattern(allbytes),

        MultipleBytesPattern(digits),
        MultipleBytesPattern(lowercase),
        MultipleBytesPattern(uppercase),
        MultipleBytesPattern(letters),
        MultipleBytesPattern(letters | digits),
        MultipleBytesPattern(letters | punctuation),
        MultipleBytesPattern(letters | digits | punctuation),
        MultipleBytesPattern(allbytes),
    ])

    result = passcheck.check(password)

    print('Entropy: %d bits' % math.ceil(result.entropy))
    print('Number of possible passwords: %s' % format_number(result.combinations))
    print('Brute force (1000 guesses/second): %s' % format_seconds(result.combinations / 1000))
    print('Brute force (1e09 guesses/second): %s' % format_seconds(result.combinations / 1e09))
