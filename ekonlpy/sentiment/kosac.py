import os
from konlpy.tag import Kkma
from ekonlpy.utils import installpath

LEXICON_PATH = '%s/data/lexicon' % installpath


class KOSAC(object):
    def __init__(self):
        self._loaddic()
        self._tagger = Kkma()

    def _loaddic(self):
        self._polarity = self._loadfile(os.path.join(LEXICON_PATH, 'kosac', 'polarity.csv'))
        self._expressive = self._loadfile(os.path.join(LEXICON_PATH, 'kosac', 'expressive-type.csv'))
        self._intensity = self._loadfile(os.path.join(LEXICON_PATH, 'kosac', 'intensity.csv'))

    def _loadfile(self, file_path, delimiter=','):
        vocab = {}
        if os.path.isfile(file_path):
            with open(file_path) as f:
                for lno, line in enumerate(f):
                    # skip header
                    if lno == 0:
                        headers = line.strip().split(delimiter)
                    else:
                        if len(line) > 0:
                            row = line.strip().split(delimiter)
                            ngram = row[0]
                            # ngram_split = tuple(ngram.split(';'))
                            data = {}
                            for i, header in enumerate(headers):
                                if i > 0:
                                    data[header] = row[i]
                            vocab[ngram] = data
        return vocab

    def morpheme(self, dataset):
        return self.align_morpheme(self._tagger.pos(dataset))

    def align_morpheme(self, morpheme):
        return ['{}/{}'.format(w, t) for w, t in morpheme]

    def percentage(self, obj):
        return {k: v / sum(obj.values()) for k, v in obj.items()}

    def calc(self, keypairs, source, target, func):
        for keypair in keypairs:
            sourcekey = keypair[0]
            targetkey = keypair[1]
            if sourcekey in source:
                sourcedata = source[sourcekey]
                sourcedata = float(sourcedata)
                target[targetkey] = func(sourcedata, target[targetkey])
        return target

    def match(self, data, pairdata, keypairs):
        ret = {k[1]: 0 for k in keypairs}
        for m in data:
            # need to make ngrams
            if m in pairdata:
                currentdata = pairdata[m]
                ret = self.calc(keypairs, currentdata, ret,
                                lambda s, t: t + s)
        return self.percentage(ret)

    def polarity(self, data):
        return self.match(data,
                          self._polarity,
                          [['COMP', 'com'],
                           ['POS', 'pos'],
                           ['NEG', 'neg'],
                           ['NEUT', 'neut'],
                           ['None', 'none']])

    def intensity(self, data):
        return self.match(data,
                          self._intensity,
                          [['High', 'high'],
                           ['Low', 'low'],
                           ['Medium', 'medium'],
                           ['None', 'none']])

    def expressive(self, data):
        return self.match(data,
                          self._expressive,
                          [['dir-action', 'dir-action'],
                           ['dir-explicit', 'dir-explicit'],
                           ['dir-speech', 'dir-speech'],
                           ['indirect', 'indirect'],
                           ['writing-device', 'writing-device']])

    def analyze(self, dataset):
        dataset = self.parse(dataset)
        ret = {}
        for analysis in ['polarity', 'intensity', 'expressive']:
            func = getattr(self, analysis)
            ret[analysis] = func(dataset)
        return ret

    def parse(self, dataset):
        tokens = []
        if type(dataset) == list:
            for t in dataset:
                tokens += self.morpheme(t)
        elif type(dataset) == str:
            tokens = self.morpheme(dataset)
        else:
            raise ValueError('The dataset has to be string or list of string type.')

        return tokens
