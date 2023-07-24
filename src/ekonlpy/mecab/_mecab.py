import logging
import os
from collections import namedtuple
from typing import Any, List, Optional, Sequence, Tuple, Union

import fugashi as _mecab

from ekonlpy.base import BaseMecab

logger = logging.getLogger(__name__)


Feature = namedtuple(
    "Feature",
    [
        "pos",
        "semantic",
        "has_jongseong",
        "reading",
        "type",
        "start_pos",
        "end_pos",
        "expression",
    ],
)
# ('합니다',
#   Feature(pos='XSA+EF', semantic=None, has_jongseong=False, reading='합니다', type='Inflect',
#           start_pos='XSA', end_pos='EF',
#           expression='하/XSA/*+ᄇ니다/EF/*')),


def _extract_feature(values: Sequence[Any]) -> Feature:
    # Reference:
    # - http://taku910.github.io/mecab/learn.html
    # - https://docs.google.com/spreadsheets/d/1-9blXKjtjeKZqsf4NzHeYJCrr49-nXeRF6D80udfcwY
    # - https://bitbucket.org/eunjeon/mecab-ko-dic/src/master/utils/dictionary/lexicon.py

    # feature = <pos>,<semantic>,<has_jongseong>,<reading>,<type>,<start_pos>,<end_pos>,<expression>
    assert len(values) == 8

    feature_values = [value if value != "*" else None for value in values]
    feature = dict(zip(Feature._fields, feature_values))
    has_jongseong = feature.get("has_jongseong")
    feature["has_jongseong"] = has_jongseong == "T"

    return Feature(**feature)


class MeCabError(Exception):
    pass


class Mecab(BaseMecab):
    backend = "fugashi"
    verbose: bool = False

    _tagger: _mecab.GenericTagger  # type: ignore

    def __init__(
        self,
        dicdir: Optional[str] = None,
        userdic_path: Optional[str] = None,
        verbose: bool = False,
        **kwargs,
    ):
        import mecab_ko_dic

        self.verbose = verbose

        DICDIR = mecab_ko_dic.DICDIR
        mecabrc = os.path.join(DICDIR, "mecabrc")

        logger.debug("MeCab uses %s backend.", self.backend)

        if not dicdir:
            dicdir = DICDIR
        MECAB_ARGS = f'-r "{mecabrc}" -d "{dicdir}" '
        if userdic_path:
            MECAB_ARGS += f'-u "{userdic_path}" '
        if self.verbose:
            logger.info(
                "Mecab uses system dictionary: %s, user dictionary: %s",
                dicdir,
                userdic_path,
            )
        try:
            self._tagger = _mecab.GenericTagger(MECAB_ARGS)  # type: ignore
            dictionary_info = self._tagger.dictionary_info
            sysdic_path = dictionary_info[0]["filename"]
            logger.debug("Mecab is loaded from %s", sysdic_path)
        except RuntimeError as e:
            raise MeCabError(
                'The MeCab dictionary does not exist at "%s". Is the dictionary correctly installed?\nYou can also try entering the dictionary path when initializing the MeCab class: "MeCab(\'/some/dic/path\')"'
                % dicdir
            ) from e
        except NameError as e:
            raise MeCabError(
                "The fugashi package is not installed. Please install fugashi with: pip install fugashi"
            ) from e

    def _parse(self, text: str) -> List[Tuple[str, Feature]]:
        return [
            (node.surface, _extract_feature(node.feature))
            for node in self._tagger(text)
        ]

    def parse(
        self,
        text: str,
        flatten: bool = True,
        include_whitespace_token: bool = False,
    ) -> List[Tuple[str, str]]:
        if flatten:
            res = [(surface, feature.pos) for surface, feature in self._parse(text)]
        else:
            res = []
            for surface, feature in self._parse(text):
                if feature.expression is None:
                    res.append((surface, feature.pos))
                else:
                    for elem in feature.expression.split("+"):
                        s = elem.split("/")
                        res.append((s[0], s[1]))
        if include_whitespace_token:
            sent_ptr = 0
            res = []

            for token, pos in res:
                if text[sent_ptr] == " ":
                    # Move pointer to whitespace token to reserve whitespace
                    # cf. to prevent double white-space, move pointer to next eojeol
                    while text[sent_ptr] == " ":
                        sent_ptr += 1
                    res.append((" ", "SP"))
                res.append((token, pos))
                sent_ptr += len(token)
        return res

    def pos(
        self,
        text: str,
        flatten: bool = True,
        include_whitespace_token: bool = False,
    ) -> List[Tuple[str, str]]:
        return self.parse(
            text, flatten=flatten, include_whitespace_token=include_whitespace_token
        )

    def tokenize(
        self,
        text: str,
        flatten: bool = True,
        include_whitespace_token: bool = False,
        strip_pos: bool = False,
        postag_delim: str = "/",
    ) -> List[str]:
        tokens = self.parse(
            text, flatten=flatten, include_whitespace_token=include_whitespace_token
        )

        return [
            token_pos[0] if strip_pos else f"{token_pos[0]}{postag_delim}{token_pos[1]}"
            for token_pos in tokens
        ]

    def morphs(self, text: str, flatten: bool = True) -> List[str]:
        return self.tokenize(
            text, flatten=flatten, strip_pos=True, include_whitespace_token=False
        )

    def nouns(
        self,
        text: Union[str, List[Tuple[str, str]]],
        flatten: bool = True,
        noun_pos: Optional[List[str]] = None,
    ) -> List[str]:
        if not noun_pos:
            noun_pos = ["NNG", "NNP", "XSN", "SL", "XR", "NNB", "NR"]
        tagged = (
            self.pos(text, flatten=flatten, include_whitespace_token=False)
            if isinstance(text, str)
            else text
        )
        return [surface for surface, pos in tagged if pos in noun_pos]


if __name__ == "__main__":
    tagger = Mecab()
    text = "아버지가 방에 들어가신다."
    print(tagger._parse(text))
    print(tagger.pos(text))
    print(tagger.morphs(text))
    print(tagger.nouns(text))
