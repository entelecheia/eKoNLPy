import os
from collections.abc import Callable
from typing import Optional, Union

from .base import LEXICON_PATH, BaseDict
from .utils import KTokenizer


class KSA(BaseDict):
    """
    Dictionary class for
    Korean Sentiment Analysis.
    """

    def init_tokenizer(self, kind: Optional[int] = None) -> None:
        self._tokenizer = KTokenizer(self._poldict)

    def init_dict(
        self, kind: Optional[int] = None, intensity_cutoff: Optional[float] = None
    ) -> None:
        path = os.path.join(LEXICON_PATH, "kosac", "polarity.csv")
        with open(path, encoding="utf-8") as f:
            for line in f:
                word = line.split(",")
                w = word[0]
                if w == "ngram":
                    continue
                if len(w) > 1:
                    n = float(word[3].strip())
                    p = float(word[6].strip())
                    s = p - n
                    if s > 0:
                        self._posdict[w] = 1
                        self._poldict[w] = s
                    elif s < 0:
                        self._negdict[w] = -1
                        self._poldict[w] = s


class KOSAC:
    def __init__(self) -> None:
        try:
            from konlpy.tag import Kkma
        except ImportError as e:
            raise ImportError("Kkma is required for KOSAC") from e  # noqa: TRY003

        self._loaddic()
        self._tagger = Kkma()
        self._ngram = 3
        self._delimiter = ";"
        self._skiptags = [
            "SF",
            "SP",
            "SS",
            "SE",
            "SO",
            "SW",
            "UN",
            "UV",
            "UE",
            "OL",
            "OH",
            "ON",
        ]

    def _loaddic(self) -> None:
        self._polarity = self._loadfile(
            os.path.join(LEXICON_PATH, "kosac", "polarity.csv")
        )
        self._expressive = self._loadfile(
            os.path.join(LEXICON_PATH, "kosac", "expressive-type.csv")
        )
        self._intensity = self._loadfile(
            os.path.join(LEXICON_PATH, "kosac", "intensity.csv")
        )

    def _loadfile(
        self, file_path: str, delimiter: str = ","
    ) -> dict[str, dict[str, str]]:
        vocab: dict[str, dict[str, str]] = {}
        with open(file_path, encoding="utf-8") as f:
            for lno, line in enumerate(f):
                # skip header
                if lno == 0:
                    headers = line.strip().split(delimiter)
                elif len(line) > 0:
                    row = line.strip().split(delimiter)
                    data = {header: row[i] for i, header in enumerate(headers) if i > 0}
                    vocab[row[0]] = data
        return vocab

    def morpheme(self, dataset: str) -> list[str]:
        return self.align_morpheme(self._tagger.pos(dataset))

    def align_morpheme(self, morpheme: list[tuple[str, str]]) -> list[str]:
        return [f"{w}/{t}" for w, t in morpheme]

    def percentage(self, obj: dict[str, float]) -> dict[str, float]:
        return {k: v / sum(obj.values()) for k, v in obj.items()}

    def calc(
        self,
        keypairs: list[list[str]],
        source: dict[str, str],
        target: dict[str, float],
        func: Callable[[float, float], float],
    ) -> dict[str, float]:
        for keypair in keypairs:
            sourcekey = keypair[0]
            if sourcekey in source:
                sourcedata = float(source[sourcekey])
                targetkey = keypair[1]
                target[targetkey] = func(sourcedata, target[targetkey])
        return target

    def match(
        self,
        data: list[str],
        pairdata: dict[str, dict[str, str]],
        keypairs: list[list[str]],
    ) -> dict[str, float]:
        ret: dict[str, float] = {k[1]: 0 for k in keypairs}
        for m in data:
            if m in pairdata:
                currentdata = pairdata[m]
                ret = self.calc(keypairs, currentdata, ret, lambda s, t: t + s)
        return self.percentage(ret)

    def polarity(self, data: list[str]) -> dict[str, float]:
        return self.match(
            data,
            self._polarity,
            [
                ["COMP", "com"],
                ["POS", "pos"],
                ["NEG", "neg"],
                ["NEUT", "neut"],
                ["None", "none"],
            ],
        )

    def intensity(self, data: list[str]) -> dict[str, float]:
        return self.match(
            data,
            self._intensity,
            [["High", "high"], ["Low", "low"], ["Medium", "medium"], ["None", "none"]],
        )

    def expressive(self, data: list[str]) -> dict[str, float]:
        return self.match(
            data,
            self._expressive,
            [
                ["dir-action", "dir-action"],
                ["dir-explicit", "dir-explicit"],
                ["dir-speech", "dir-speech"],
                ["indirect", "indirect"],
                ["writing-device", "writing-device"],
            ],
        )

    def analyze(self, dataset: Union[str, list[str]]) -> dict[str, dict[str, float]]:
        dataset = self.parse(dataset)
        ret: dict[str, dict[str, float]] = {}
        for analysis in ["polarity", "intensity", "expressive"]:
            func = getattr(self, analysis)
            ret[analysis] = func(dataset)
        return ret

    def parse(self, dataset: Union[str, list[str]]) -> list[str]:
        tokens: list[str] = []
        if isinstance(dataset, list):
            for t in dataset:
                tokens += self.morpheme(t)
        elif isinstance(dataset, str):
            tokens = self.morpheme(dataset)
        else:
            raise TypeError(  # noqa: TRY003
                "The dataset has to be string or list of string type."
            )

        return self.ngramize(tokens)

    def ngramize(self, tokens: list[str]) -> list[str]:
        ngram_tokens: list[str] = []
        tokens = [w for w in tokens if w.split("/")[1] not in self._skiptags]
        for pos in range(len(tokens)):
            for gram in range(1, self._ngram + 1):
                if token := self.get_ngram(tokens, pos, gram):
                    ngram_tokens.append(token)
        return ngram_tokens

    def get_ngram(self, tokens: list[str], pos: int, gram: int) -> Optional[str]:
        if pos < 0:
            return None
        if pos + gram > len(tokens):
            return None
        token = tokens[pos]
        for i in range(1, gram):
            token += self._delimiter + tokens[pos + i]
        return token
