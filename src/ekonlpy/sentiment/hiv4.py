from typing import Optional

import pandas as pd

from .base import LEXICON_PATH, BaseDict
from .utils import Tokenizer


class HIV4(BaseDict):
    """
    Dictionary class for Harvard IV-4.
    See also http://www.wjh.harvard.edu/~inquirer/

    The terms for the dictionary are stemmed by the default tokenizer.
    """

    PATH = f"{LEXICON_PATH}/HIV-4.csv"

    def init_tokenizer(
        self, kind: Optional[int] = None, intensity_cutoff: Optional[float] = None
    ) -> None:
        """Initialize the default stemming tokenizer.

        :param kind: Unused; kept for interface compatibility
        :param intensity_cutoff: Unused; kept for interface compatibility
        """
        self._tokenizer = Tokenizer()

    def init_dict(
        self, kind: Optional[int] = None, intensity_cutoff: Optional[float] = None
    ) -> None:
        """Load the Harvard IV-4 lexicon and initialize the polarity dictionaries.

        :param kind: Unused; kept for interface compatibility
        :param intensity_cutoff: Unused; kept for interface compatibility
        """
        # BaseDict loads the dictionary before assigning the public tokenizer.
        # Keep lexicon stemming independent of a caller-provided tokenizer.
        tokenizer = Tokenizer()
        data = pd.read_csv(self.PATH, low_memory=False)
        for category in ["Positiv", "Negativ"]:
            terms = data["Entry"][data[category] == category]
            for t in terms:
                t = tokenizer.tokenize(t)
                if len(t) > 0:
                    if category == "Positiv":
                        self._posdict[t[0]] = 1
                    else:
                        self._negdict[t[0]] = -1
