import pandas as pd

from .base import LEXICON_PATH, BaseDict
from .utils import Tokenizer


class LM(BaseDict):
    """
    Dictionary class for
    Loughran and McDonald Financial Sentiment Dictionaries.

    See also https://www3.nd.edu/~mcdonald/Word_Lists.html

    The terms for the dictionary are stemmed by the default tokenizer.
    """

    PATH = "%s/LM.csv" % LEXICON_PATH

    def init_tokenizer(self, kind=None, intensity_cutoff=None):
        self._tokenizer = Tokenizer()

    def init_dict(self, kind=None):
        data = pd.read_csv(self.PATH, low_memory=False)
        for category in ["Positive", "Negative"]:
            terms = data["Word"][data[category] > 0]
            if category == "Positive":
                for t in terms:
                    t = self.tokenize(t)
                    if len(t) > 0:
                        self._posdict[t[0]] = 1
            else:
                for t in terms:
                    t = self.tokenize(t)
                    if len(t) > 0:
                        self._negdict[t[0]] = -1
