import logging
import os
from collections import namedtuple

log = logging.getLogger(__name__)


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


def _extract_feature(values):
    # Reference:
    # - http://taku910.github.io/mecab/learn.html
    # - https://docs.google.com/spreadsheets/d/1-9blXKjtjeKZqsf4NzHeYJCrr49-nXeRF6D80udfcwY
    # - https://bitbucket.org/eunjeon/mecab-ko-dic/src/master/utils/dictionary/lexicon.py

    # feature = <pos>,<semantic>,<has_jongseong>,<reading>,<type>,<start_pos>,<end_pos>,<expression>
    assert len(values) == 8

    values = [value if value != "*" else None for value in values]
    feature = dict(zip(Feature._fields, values))
    feature["has_jongseong"] = {"T": True, "F": False}.get(feature["has_jongseong"])

    return Feature(**feature)


class MeCabError(Exception):
    pass


class MeCab:  # APIs are inspried by KoNLPy
    def __init__(
        self,
        dicdir=None,
        userdic_path=None,
        verbose=False,
        **kwargs,
    ):
        import mecab_ko_dic

        self.dicdir = None
        self.userdic_path = None
        self.verbose = verbose

        DICDIR = mecab_ko_dic.DICDIR
        mecabrc = os.path.join(DICDIR, "mecabrc")

        if self.verbose:
            log.info(f"MeCab uses {self.backend} as backend.")

        if not dicdir:
            dicdir = DICDIR
        self.dicdir = dicdir
        MECAB_ARGS = '-r "{}" -d "{}" '.format(mecabrc, dicdir)
        if userdic_path:
            self.userdic_path = userdic_path
            MECAB_ARGS += '-u "{}" '.format(userdic_path)
        if self.verbose:
            log.info(
                f"Mecab uses system dictionary: {dicdir}, user dictionary: {userdic_path}"
            )
        try:
            try:
                import fugashi as _mecab
            except ImportError:
                raise ImportError(
                    "\n"
                    "You must install `fugashi` to use MeCab backend.\n"
                    "Please install it with `pip install fugashi`.\n"
                )
            self.tagger = _mecab.GenericTagger(MECAB_ARGS)
            self.dictionary_info = self.tagger.dictionary_info
            self.sysdic_path = self.dictionary_info[0]["filename"]
        except RuntimeError:
            raise Exception(
                'The MeCab dictionary does not exist at "%s". Is the dictionary correctly installed?\nYou can also try entering the dictionary path when initializing the MeCab class: "MeCab(\'/some/dic/path\')"'
                % self.dicdir
            )
        except NameError:
            raise Exception("Check if MeCab is installed correctlly.")

    def parse(self, text):
        return [
            (node.surface, _extract_feature(node.feature)) for node in self.tagger(text)
        ]

    def pos(
        self,
        sentence,
        flatten=True,
        concat_surface_and_pos=False,
        include_whitespace_token=False,
    ):
        sentence = sentence.strip()
        if include_whitespace_token:
            sent_ptr = 0
            res = []

            for token, pos in self._pos(sentence, flatten=flatten):
                if sentence[sent_ptr] == " ":
                    # Move pointer to whitespace token to reserve whitespace
                    # cf. to prevent double white-space, move pointer to next eojeol
                    while sentence[sent_ptr] == " ":
                        sent_ptr += 1
                    res.append((" ", "SP"))
                res.append((token, pos))
                sent_ptr += len(token)
        else:
            res = self._pos(sentence, flatten=flatten)

        return [s[0] + "/" + s[1] if concat_surface_and_pos else s for s in res]

    def _pos(self, sentence, flatten=True):
        if flatten:
            return [(surface, feature.pos) for surface, feature in self.parse(sentence)]
        else:
            res = []
            for surface, feature in self.parse(sentence):
                if feature.expression is None:
                    res.append((surface, feature.pos))
                else:
                    for elem in feature.expression.split("+"):
                        s = elem.split("/")
                        res.append((s[0], s[1]))
            return res

    def morphs(self, sentence, flatten=True, include_whitespace_token=True):
        return [
            surface
            for surface, _ in self.pos(
                sentence,
                flatten=flatten,
                concat_surface_and_pos=False,
                include_whitespace_token=include_whitespace_token,
            )
        ]

    def nouns(
        self,
        sentence,
        flatten=True,
        include_whitespace_token=True,
        noun_pos=["NNG", "NNP", "XSN", "SL", "XR", "NNB", "NR"],
    ):
        return [
            surface
            for surface, pos in self.pos(
                sentence,
                flatten=flatten,
                concat_surface_and_pos=False,
                include_whitespace_token=include_whitespace_token,
            )
            if pos in noun_pos
        ]


if __name__ == "__main__":
    tagger = MeCab()
    text = "아버지가 방에 들어가신다."
    print(tagger.parse(text))
    print(tagger.pos(text))
    print(tagger.morphs(text))
    print(tagger.nouns(text))
