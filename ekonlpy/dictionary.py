term_tags = {
    'COUNTRY': '국가',
    'INDUSTRY': '산업용어',
    'PERSON': '사람',
    'SECTOR': '산업/업종',
    'ENTITY': '기업/종목',
    'GENERIC': '범용어',
    'GEO': '지역명'
}


class TermDictionary:
    def __init__(self):
        self._pos2words = {}

    def add_dictionary(self, words, tag):
        if type(words) == str:
            words = [words]
        wordset = self._pos2words.get(tag, set())
        wordset.update(set(words))
        self._pos2words[tag] = wordset

    def load_dictionary(self, fname, tag):
        def load(fname):
            try:
                with open(fname, encoding='utf-8') as f:
                    words = {word.strip().lower() for word in f}
                    return words
            except Exception as e:
                print('load_dictionary error: %s' % e)
                return []

        wordset = self._pos2words.get(tag, set())
        wordset.update(load(fname))
        self._pos2words[tag] = wordset

    def get_tags(self, word):
        # return {tag for tag, words in self._pos2words.items() if word in words}
        for tag, words in self._pos2words.items():
            if word.lower() in words:
                return tag

    def check_tag(self, word, tag):
        for tg, words in self._pos2words.items():
            if word.lower() in words:
                tag = tg
                break
        tag = tag.split('+')[0]
        return tag

    def is_tag(self, word, tag):
        return word.lower() in self._pos2words.get(tag, {})

    def exists(self, word, tag=None):
        if tag in self._pos2words:
            return True if word.lower() in self._pos2words[tag] else False
        else:
            for tag, words in self._pos2words.items():
                if word.lower() in words:
                    return True
            return False
