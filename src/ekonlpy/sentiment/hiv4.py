import pandas as pd

from .base import LEXICON_PATH, BaseDict
from .utils import Tokenizer


class HIV4(BaseDict):
    """
    Dictionary class for Harvard IV-4.
    See also http://www.wjh.harvard.edu/~inquirer/

    The terms for the dictionary are stemmed by the default tokenizer.
    """

    PATH = "%s/HIV-4.csv" % LEXICON_PATH

    def init_tokenizer(self, kind=None, intensity_cutoff=None):
        self._tokenizer = Tokenizer()

    def init_dict(self, kind=None):
        data = pd.read_csv(self.PATH, low_memory=False)
        for category in ["Positiv", "Negativ"]:
            terms = data["Entry"][data[category] == category]
            if category == "Positiv":
                for t in terms:
                    t = self.tokenize(t)
                    if len(t) > 0:
                        self._posdict[t[0]] = 1
            else:
                for t in terms:
                    t = self.tokenize(t)
                    if len(t) > 0:
                        self._negdict[t[0]] = -1
