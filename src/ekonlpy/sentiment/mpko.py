from typing import ClassVar, Optional

from .base import IntensityLexiconDict
from .utils import MPTokenizer


class MPKO(IntensityLexiconDict):
    """
    Dictionary class for
    Korean Monetary Policy Sentiment Analysis.

    ``Positive`` means ``hawkish`` and ``Negative`` means ``dovish``.
    """

    LEXICON_DIR: ClassVar[str] = "mpko"
    MAX_INTENSITY_CUTOFF: ClassVar[float] = 2
    KINDS: ClassVar[dict[int, str]] = {
        0: "mp_polarity_lexicon_mkt.csv",
        1: "mp_polarity_lexicon_lex.csv",
        3: "mp_polarity_lexicon_mkt_n3.csv",
        7: "mp_polarity_lexicon_mkt_n7.csv",
    }
    INTENSITY_KINDS: ClassVar[dict[int, float]] = {0: 1.3, 1: 1.1, 3: 1.3, 7: 1.3}

    def init_tokenizer(self, kind: Optional[int] = None) -> None:
        """Initialize the n-gram tokenizer for the selected lexicon kind.

        :param kind: A parameter to select a lexicon file
        """
        self._tokenizer = MPTokenizer(kind, self._poldict)
