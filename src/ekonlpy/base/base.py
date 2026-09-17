import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BaseMecab:
    """Abstract class for MeCab tagger"""

    def parse(
        self,
        text: str,
    ) -> list[tuple[str, str]]:
        """Tag the text and return (surface, pos) tuples. Must be implemented by subclasses.

        :param text: The input text to tag
        :return: A list of (surface, pos) tuples
        :raises NotImplementedError: Always; subclasses must override this method
        """
        raise NotImplementedError

    def pos(
        self,
        text: str,
    ) -> list[tuple[str, str]]:
        """Return POS-tagged tokens for the given text.

        :param text: The input text to tag
        :return: A list of (surface, pos) tuples
        """
        return self.parse(text)

    def tokenize(
        self,
        text: str,
        strip_pos: bool = False,
        postag_delim: str = "/",
    ) -> list[str]:
        """Tokenize the text into "surface/pos" strings or bare surfaces.

        :param text: The input text to tokenize
        :param strip_pos: Whether to drop the POS tags from the tokens
        :param postag_delim: Delimiter between a surface and its POS tag
        :return: A list of token strings
        """
        tokens = self.parse(text)

        return [
            token_pos[0] if strip_pos else f"{token_pos[0]}{postag_delim}{token_pos[1]}"
            for token_pos in tokens
        ]

    def morphs(self, text: str) -> list[str]:
        """Return the morphemes (surfaces without POS tags) of the given text.

        :param text: The input text to analyze
        :return: A list of morpheme strings
        """
        return self.tokenize(text, strip_pos=True)

    def nouns(
        self,
        text: str,
        flatten: bool = True,
        noun_pos: Optional[list[str]] = None,
    ) -> list[str]:
        """Return the nouns of the given text.

        :param text: The input text to analyze
        :param flatten: Unused; kept for interface compatibility
        :param noun_pos: POS tags considered as nouns
        :return: A list of noun surfaces
        """
        if not noun_pos:
            noun_pos = []
        return [surface for surface, pos in self.pos(text) if pos in noun_pos]
