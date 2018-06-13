import os
from ekonlpy.sentiment.base import LEXICON_PATH, BaseDict
from ekonlpy.sentiment.utils import MPTokenizer, MPTokenizerx


class MPKO(BaseDict):
    '''
    Dictionary class for
    Korean Monetary Policy Sentiment Analysis.

    ``Positive`` means ``hawkish`` and ``Negative`` means ``dovish``.
    '''

    KINDS = {0: 'mp_polarity_lexicon_ma.csv',
             1: 'mp_polarity_lexicon_la.csv'
             }

    def init_tokenizer(self, kind=None):
        self._tokenizer = MPTokenizer(kind)

    def init_dict(self, kind=None):
        kind = kind if kind in self.KINDS.keys() else 0
        print('Initialize the dictionary using a lexicon file: {}'.format(self.KINDS[kind]))
        path = os.path.join(LEXICON_PATH, 'mpko', self.KINDS[kind])
        with open(path, encoding='utf-8') as f:
            for line in f:
                word = line.split(',')
                w = word[0]
                if w == 'word':
                    continue
                p = float(word[1].strip())
                s = float(word[2].strip())
                if len(w) > 1:
                    self._poldict[w] = s
                    if p > 0:
                        self._posdict[w] = 1
                    elif p < 0:
                        self._negdict[w] = -1


class MPKOx(BaseDict):
    '''
    Dictionary class for
    Korean Monetary Policy Sentiment Analysis.

    ``Positive`` means ``hawkish`` and ``Negative`` means ``dovish``.
    '''

    KINDS = {0: 'mp_polarities_call_5gram.csv',
             1: 'mp_polarities_w2c5_w5.csv'
             }

    def init_tokenizer(self, kind=None):
        self._tokenizer = MPTokenizerx(kind)

    def init_dict(self, kind=None):
        kind = kind if kind in self.KINDS.keys() else 0
        print('Initialize the dictionary using a lexicon file: {}'.format(self.KINDS[kind]))
        path = os.path.join(LEXICON_PATH, 'mpkox', self.KINDS[kind])
        with open(path, encoding='utf-8') as f:
            for line in f:
                word = line.split(',')
                w = word[0]
                if w == 'word':
                    continue
                p = float(word[1].strip())
                s = float(word[2].strip())
                if len(w) > 1:
                    self._poldict[w] = s
                    if p > 0:
                        self._posdict[w] = 1
                    elif p < 0:
                        self._negdict[w] = -1


