import os.path

from passcheck.utils import is_binary


class Pattern(object):

    def __init__(self, title):
        self.title = title

    def __str__(self):
        return self.title


class MultipleBytesPattern(Pattern):

    def __init__(self, title, superset: set):
        super().__init__(title)
        self.superset = superset

    def matches(self, value):
        return value.unique_bytes <= self.superset

    def combinations(self, value):
        k = len(self.superset)
        n = len(value.bytes)
        return sum(k**i for i in range(1, n + 1))


class SingleBytePattern(MultipleBytesPattern):

    def matches(self, value):
        return len(value.bytes) > 1 and value.unique_bytes_count == 1 and super().matches(value)

    def combinations(self, value):
        k = len(self.superset)
        n = len(value.bytes)
        return k * n


class DictPattern(Pattern):

    def __init__(self, title, words, ranked=False):
        super().__init__(title)
        self.words = words
        self.ranked = ranked

    def matches(self, value):
        return len(value.bytes) > 1 and value.bytes in self.words

    def combinations(self, value):
        return self.words[value.bytes] if self.ranked else len(self.words)


class TitleCaseDictPattern(DictPattern):

    def matches(self, value):
        if len(value.bytes) <= 1:
            return False
        v = value.bytes
        v = v[:1].lower() + v[1:]
        return v in self.words

    def combinations(self, value):
        return super().combinations(value) * 2


class CaseInsensitiveDictPattern(DictPattern):

    def matches(self, value):
        return len(value.bytes) > 1 and value.bytes.lower() in self.words

    def combinations(self, value):
        c = 0
        for w in self.words:
            c += 2**len(w)
            if self.ranked and w == value.bytes.lower():
                return c
        return c


class HunspellPattern(Pattern):

    def __init__(self, title, dpath, apath, required=True):
        super().__init__(title)

        self.dpath = dpath
        self.apath = apath

        hunspell = self.import_hunspell(required)

        if required or (os.path.exists(dpath) and os.path.exists(apath)):
            self.hs = hunspell.HunSpell(dpath, apath)
            with open(dpath, encoding=self.hs.get_dic_encoding()) as f:
                self.word_count = int(f.readline().strip())
        else:
            self.hs = None
            self.word_count = 0

    def import_hunspell(self, required=True):
        try:
            import hunspell
        except ImportError:
            if required:
                raise
            return None
        else:
            return hunspell

    def matches(self, value):
        if self.hs is None or len(value.bytes) <= 1 or is_binary(value.bytes):
            return False
        try:
            return self.hs.spell(value.bytes.decode('utf-8'))
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False

    def combinations(self, value):
        v = value.bytes.decode('utf-8')
        if v[0].isupper() and v[:1].islower():
            return self.word_count * 2
        elif not v.islower():
            count = 0
            with open(self.dpath, encoding=self.hs.get_dic_encoding()) as f:
                for line in f:
                    word, _ = (line.strip() + '/').split('/', 1)
                    count += 2**len(word)
            return count
        else:
            return self.word_count


class SequencePatter(Pattern):

    def __init__(self, title, sequence: bytes):
        super().__init__(title)
        self.sequence = sequence.encode() if isinstance(sequence, str) else sequence

    def matches(self, value):
        return len(value.bytes) > 1 and value.bytes in self.sequence

    def combinations(self, value):
        size = self.sequence.index(value.bytes) + len(value.bytes)
        # Basically this tells how many times you need to run:
        #
        #   for i in range(size):
        #       for j in range(i, size):
        #           yield seq[i:j+1]
        #
        return int(size * (size + 1) / 2)
