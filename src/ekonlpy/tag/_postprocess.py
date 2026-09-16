from typing import Optional, Union

from ._mecab import Mecab


class Postprocessor:
    def __init__(
        self,
        base_tagger: Mecab,
        stopwords: Optional[list[str]] = None,
        passwords: Optional[list[str]] = None,
        passtags: Optional[list[str]] = None,
        replace: Optional[
            dict[Union[str, tuple[str, str]], Union[str, tuple[str, str]]]
        ] = None,
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

    def tag(self, phrase: str) -> list[tuple[str, str]]:
        """
        Tag the given phrase using the base tagger and apply post-processing filters.

        :param phrase: Input phrase to be tagged
        :return: List of tagged words after applying filters
        """

        def to_replace(
            w: tuple[str, str],
            replace: dict[Union[str, tuple[str, str]], Union[str, tuple[str, str]]],
        ) -> tuple[str, str]:
            if w in replace:
                w_ = replace[w]
            elif w[0] in replace:
                w_ = replace[w[0]]
            else:
                return w
            return (w_, w[1]) if isinstance(w_, str) else w_

        words = self.base_tagger.pos(phrase)
        if self.stopwords:
            words = [
                w
                for w in words
                if w not in self.stopwords and w[0] not in self.stopwords
            ]
        if self.passwords:
            words = [
                w for w in words if ((w in self.passwords) or (w[0] in self.passwords))
            ]
        if self.passtags:
            words = [w for w in words if w[1] in self.passtags]
        if self.replace:
            words = [to_replace(w, self.replace) for w in words]
        return words
