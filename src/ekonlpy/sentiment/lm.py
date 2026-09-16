from typing import Optional

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

    PATH = f"{LEXICON_PATH}/LM.csv"

    def init_tokenizer(
        self, kind: Optional[int] = None, intensity_cutoff: Optional[float] = None
    ) -> None:
        self._tokenizer = Tokenizer()

    def init_dict(
        self, kind: Optional[int] = None, intensity_cutoff: Optional[float] = None
    ) -> None:
        # BaseDict loads the dictionary before assigning the public tokenizer.
        # Keep lexicon stemming independent of a caller-provided tokenizer.
        tokenizer = Tokenizer()
        data = pd.read_csv(self.PATH, low_memory=False)
        for category in ["Positive", "Negative"]:
            terms = data["Word"][data[category] > 0]
            for t in terms:
                t = tokenizer.tokenize(t)
                if len(t) > 0:
                    if category == "Positive":
                        self._posdict[t[0]] = 1
                    else:
                        self._negdict[t[0]] = -1
