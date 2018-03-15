import pandas as pd
from ekonlpy.sentiment.base import LEXICON_PATH, BaseDict


class MPKO(BaseDict):
    '''
    Dictionary class for
    Korean Monetary Policy.
    '''

    PATH = '%s/MPKO.csv' % LEXICON_PATH

    def init_dict(self):
        with open(self.PATH, encoding='utf-8') as f:
            for line in f:
                w, p = line.split(',')
                if w == 'word':
                    continue
                p = float(p.strip())
                if len(w) > 1 and p > 0:
                    self._posdict[w] = p
                elif len(w) > 1 and p < 0:
                    self._negdict[w] = p
