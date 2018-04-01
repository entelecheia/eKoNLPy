import os
from ekonlpy.sentiment.base import LEXICON_PATH, BaseDict
from ekonlpy.sentiment.utils import MPTokenizer


class MPKO(BaseDict):
    '''
    Dictionary class for
    Korean Monetary Policy Sentiment Analysis.

    ``Positive`` means ``hawkish`` and ``Negative`` means ``dovish``.
    '''

    KINDS = {0: 'MPS_polarities_bi_pt_w5.csv',
             1: 'MPS_polarities_GB3Y2_5gram.csv',
             2: 'MPS_polarities_GB3Y_5gram.csv',
             3: 'MPS_polarities_call2_5gram.csv',
             4: 'MPS_polarities_call_5gram.csv'
             }

    def init_tokenizer(self):
        self._tokenizer = MPTokenizer()

    def init_dict(self, kind=None):
        kind = kind if kind in self.KINDS.keys() else 0
        print('Initialize the dictionary using a lexicon file: {}'.format(self.KINDS[kind]))
        path = os.path.join(LEXICON_PATH, self.KINDS[kind])
        with open(path, encoding='utf-8') as f:
            for line in f:
                word = line.split(',')
                w = word[0]
                if w == 'word':
                    continue
                p = float(word[1].strip())
                if len(w) > 1 and p > 0:
                    self._posdict[w] = p
                elif len(w) > 1 and p < 0:
                    self._negdict[w] = p
