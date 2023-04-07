from typing import Dict, List, Optional, Tuple, Union

from ._mecab import Mecab


class Postprocessor:
    def __init__(
        self,
        base_tagger: Mecab,
        stopwords: Optional[List[str]] = None,
        passwords: Optional[List[str]] = None,
        passtags: Optional[List[str]] = None,
        replace: Optional[Dict[str, Union[str, Tuple[str, str]]]] = None,
    ):
        """
        Initialize the Postprocessor class.

        :param base_tagger: Instance of the base tagger
        :param stopwords: List of stopwords to be filtered out, defaults to None
        :param passwords: List of password-protected words to be kept, defaults to None
        :param passtags: List of tags to be kept, defaults to None
        :param replace: Dictionary of words and their replacements, defaults to None
        """
        self.base_tagger = base_tagger
        self.stopwords = stopwords
        self.passwords = passwords
        self.passtags = passtags
        self.replace = replace

    def tag(self, phrase: str) -> List[Tuple[str, str]]:
        """
        Tag the given phrase using the base tagger and apply post-processing filters.

        :param phrase: Input phrase to be tagged
        :return: List of tagged words after applying filters
        """

        def to_replace(w: Tuple[str, str]) -> Tuple[str, str]:
            if w in self.replace:
                w_ = self.replace[w]
            elif w[0] in self.replace:
                w_ = self.replace[w[0]]
            else:
                return w
            return (w_, w[1]) if isinstance(w_, str) else w_

        words = self.base_tagger.pos(phrase)
        if self.stopwords:
            words = [
                w
                for w in words
                if not ((w in self.stopwords) or (w[0] in self.stopwords))
            ]
        if self.passwords:
            words = [
                w for w in words if ((w in self.passwords) or (w[0] in self.passwords))
            ]
        if self.passtags:
            words = [w for w in words if w[1] in self.passtags]
        if self.replace:
            words = [to_replace(w) for w in words]
        return words
