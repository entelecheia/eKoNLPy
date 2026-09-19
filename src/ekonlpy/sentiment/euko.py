from typing import ClassVar, Optional

from .base import IntensityLexiconDict
from .utils import MPTokenizer


class EUKO(IntensityLexiconDict):
    """
    Dictionary class for
    Korean Economic Uncertainty Analysis.

    ``Positive`` means ``hawkish`` and ``Negative`` means ``dovish``.
    """

    LEXICON_DIR: ClassVar[str] = "euko"
    MAX_INTENSITY_CUTOFF: ClassVar[float] = 3
    KINDS: ClassVar[dict[int, str]] = {
        0: "mp_uncertainty_lexicon_mkt.csv",
        1: "mp_uncertainty_lexicon_lex.csv",
    }
    INTENSITY_KINDS: ClassVar[dict[int, float]] = {0: 2.0, 1: 1.3}

    def init_tokenizer(self, kind: Optional[int] = None) -> None:
        """Initialize the n-gram tokenizer for the selected lexicon kind.

        :param kind: A parameter to select a lexicon file
        """
        self._tokenizer = MPTokenizer(kind, self._poldict, keep_overlapping_ngram=True)
