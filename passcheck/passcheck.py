import math
import operator
import string

from itertools import combinations
from collections import defaultdict

from passcheck import patterns as pt
from passcheck import wordlist


class Value(object):

    def __init__(self, value: str):
        self.bytes = value
        self.unique_bytes = set(value)
        self.unique_bytes_count = len(self.unique_bytes)


class Result(object):

    def __init__(self, pattern, value):
        self.value = value
        self.pattern = pattern
        self.combinations = pattern.combinations(value)
        self.entropy = math.log2(self.combinations)

    def __repr__(self):
        return '<%s entropy=%.04f, pattern=%s>' % (repr(self.value.bytes).lstrip('b'), self.entropy, self.pattern)


class DefaultPattern(pt.Pattern):

    def __init__(self, title='default'):
        super().__init__(title)

    def matches(self, value):
        return True

    def combinations(self, value):
        k = 256
        n = len(value.bytes)
        return sum(k**i for i in range(1, n + 1))


class PassCheck(object):

    def __init__(self, patterns, debug=False):
        self.patterns = patterns
        self.debug = debug

    def get_result(self, value):
        results = []
        value = Value(value.encode()) if isinstance(value, str) else Value(value)
        for pattern in self.patterns:
            if pattern.matches(value):
                result = Result(pattern, value)
                results.append((result.entropy, result))
        if results:
            results.sort(key=operator.itemgetter(0))
            return results[0][1]
        else:
            return Result(DefaultPattern(), value)

    def check(self, password):
        tree = defaultdict(list)
        for i, j in combinations(range(len(password) + 1), 2):
            value = password[i:j]
            result = self.get_result(value)
            length = len(result.value.bytes)
            entropy = result.entropy / length + 1 / length
            tree[i].append((j, entropy, result))
        return next(self.compositions(tree))

    def compositions(self, tree, i=0):
        if self.debug:
            for _, e, r in sorted(tree[i], key=operator.itemgetter(1)):
                print('%.04f  %s' % (e, r))
            print('-----')
        for j, entropy, result in sorted(tree[i], key=operator.itemgetter(1)):
            if j in tree:
                for row in self.compositions(tree, j):
                    yield (result,) + row
            else:
                yield (result,)


def get_default_passcheck(debug=False):
    digits = set(string.digits.encode())
    hexdigits_lowercase = set(string.hexdigits.lower().encode())
    hexdigits_uppercase = set(string.hexdigits.upper().encode())
    lowercase = set(string.ascii_lowercase.encode())
    uppercase = set(string.ascii_uppercase.encode())
    letters = set(string.ascii_letters.encode())
    punctuation = set(string.punctuation.encode())
    allbytes = set(range(256))

    cracklib_words = wordlist.load('/usr/share/dict/cracklib-small', required=False)
    unix_words = wordlist.load('/usr/share/dict/words', required=False)

    return PassCheck([
        pt.HunspellPattern('hunspell dictionary (lt)', '/usr/share/hunspell/lt_LT.dic', '/usr/share/hunspell/lt_LT.aff', required=False),  # noqa
        pt.HunspellPattern('hunspell dictionary (us)', '/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff', required=False),  # noqa

        pt.DictPattern('cracklib dictionary', cracklib_words),
        pt.TitleCaseDictPattern('cracklib dictionary (title)', cracklib_words),
        pt.CaseInsensitiveDictPattern('cracklib dictionary (case-insensitive)', cracklib_words),

        pt.DictPattern('unix words', unix_words),
        pt.TitleCaseDictPattern('unix words (title)', unix_words),
        pt.CaseInsensitiveDictPattern('unix words (case insensitive)', unix_words),

        pt.SequencePatter('123... sequence', string.digits),
        pt.SequencePatter('abc... sequence', string.ascii_lowercase),
        pt.SequencePatter('ABC... sequence', string.ascii_uppercase),
        pt.SequencePatter('abc...ABC.. sequence', string.ascii_letters),

        pt.SingleBytePattern('single digit repeated', digits),
        pt.SingleBytePattern('single lower case letter repeated', lowercase),
        pt.SingleBytePattern('single upper case letter repeated', uppercase),
        pt.SingleBytePattern('single letter repeated (case insensitive)', letters),
        pt.SingleBytePattern('single letter or digit repeated (case insensitive)', letters | digits),
        pt.SingleBytePattern('single letter or punctuation symbol repeated (case insensitive)', letters | punctuation),
        pt.SingleBytePattern('single letter, digit or punctuation repeated (case insensitive)', letters | digits | punctuation),  # noqa
        pt.SingleBytePattern('single byte repeated', allbytes),

        pt.MultipleBytesPattern('digits', digits),
        pt.MultipleBytesPattern('symbols', punctuation),
        pt.MultipleBytesPattern('hex digits (lower case)', hexdigits_lowercase),
        pt.MultipleBytesPattern('hex digits (upper case)', hexdigits_uppercase),
        pt.MultipleBytesPattern('lower case letters', lowercase),
        pt.MultipleBytesPattern('upper case letters', uppercase),
        pt.MultipleBytesPattern('lower or upper case letters', letters),
        pt.MultipleBytesPattern('lower or upper case letters and digits', letters | digits),
        pt.MultipleBytesPattern('lower or upper case letters and punctuation', letters | punctuation),
        pt.MultipleBytesPattern('lower or upper case letters, digits and punctuation', letters | digits | punctuation),
        pt.MultipleBytesPattern('sequence of bytes', allbytes),
    ], debug=debug)
