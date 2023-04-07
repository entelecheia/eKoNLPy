import os

from .base import LEXICON_PATH, BaseDict
from .utils import MPTokenizer


class MPKO(BaseDict):
    """
    Dictionary class for
    Korean Monetary Policy Sentiment Analysis.

    ``Positive`` means ``hawkish`` and ``Negative`` means ``dovish``.
    """

    KINDS = {
        0: "mp_polarity_lexicon_mkt.csv",
        1: "mp_polarity_lexicon_lex.csv",
        3: "mp_polarity_lexicon_mkt_n3.csv",
        7: "mp_polarity_lexicon_mkt_n7.csv",
    }
    INTENSITY_KINDS = {0: 1.3, 1: 1.1, 3: 1.3, 7: 1.3}

    def init_tokenizer(self, kind=None):
        self._tokenizer = MPTokenizer(kind, self._poldict)

    def init_dict(self, kind=None, intensity_cutoff=None):
        kind = kind if kind in self.KINDS.keys() else 0
        if intensity_cutoff is not None:
            self._intensity_cutoff = intensity_cutoff
        else:
            if kind in self.INTENSITY_KINDS.keys():
                self._intensity_cutoff = self.INTENSITY_KINDS[kind]
            else:
                self._intensity_cutoff = 1.1
        self._intensity_cutoff = min(2, self._intensity_cutoff)
        # print('Initialize the dictionary using a lexicon file: {}'.format(self.KINDS[kind]))
        path = os.path.join(LEXICON_PATH, "mpko", self.KINDS[kind])
        with open(path, encoding="utf-8") as f:
            for line in f:
                word = line.split(",")
                w = word[0]
                if w == "word":
                    continue
                p = float(word[1].strip())
                s = float(word[2].strip())
                i = float(word[5].strip())
                if len(w) > 1 and i > self._intensity_cutoff:
                    self._poldict[w] = s
                    if p > 0:
                        self._posdict[w] = 1
                    elif p < 0:
                        self._negdict[w] = -1
