import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class BaseMecab:
    """Abstract class for MeCab tagger"""

    def parse(
        self,
        text: str,
    ) -> List[Tuple[str, str]]:
        raise NotImplementedError

    def pos(
        self,
        text: str,
    ) -> List[Tuple[str, str]]:
        return self.parse(text)

    def tokenize(
        self,
        text: str,
        strip_pos: bool = False,
        postag_delim: str = "/",
    ) -> List[str]:
        tokens = self.parse(text)

        return [
            token_pos[0] if strip_pos else f"{token_pos[0]}{postag_delim}{token_pos[1]}"
            for token_pos in tokens
        ]

    def morphs(self, text: str) -> List[str]:
        return self.tokenize(text, strip_pos=True)

    def nouns(
        self,
        text: str,
        flatten: bool = True,
        noun_pos: Optional[List[str]] = None,
    ) -> List[str]:
        if not noun_pos:
            noun_pos = []
        return [surface for surface, pos in self.pos(text) if pos in noun_pos]
