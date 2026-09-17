"""
This module contains methods to tokenize sentences.
"""

import abc
import os
import re
from collections.abc import Mapping, Sequence
from typing import ClassVar, Optional, TypedDict, Union

import nltk

from ..tag import Mecab
from .base import LEXICON_PATH


class BaseTokenizer(abc.ABC):
    """
    An abstract class for tokenize text.
    """

    @abc.abstractmethod
    def tokenize(self, text: str) -> list[str]:
        """Return tokenized temrs.

        :type text: str

        :returns: list
        """
        pass

    # @abc.abstractmethod
    # def ngramize(self, tokens):
    #     '''Return n-gramized temrs.
    #
    #     :type tokens: list of tokens
    #
    #     :returns: list
    #     '''
    #     pass


class KTokenizer(BaseTokenizer):
    """
    The default tokenizer for KSA sub class.
    The output of the tokenizer is tagged by Kkma.
    """

    def __init__(self, vocab: Optional[Mapping[str, object]] = None) -> None:
        """Initialize the tokenizer with the Kkma tagger and an optional vocabulary.

        :param vocab: A vocabulary mapping; only n-grams in it are kept when given
        :raises ImportError: If konlpy is not installed
        """
        try:
            from konlpy.tag import Kkma
        except ImportError as e:
            raise ImportError(  # noqa: TRY003
                "KTokenizer requires konlpy. "
                "Please install it with `pip install konlpy`."
            ) from e

        self._tagger = Kkma()
        self._vocab = vocab
        self._min_ngram = 1
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

    def tokenize(self, text: Union[str, list[str]]) -> list[str]:
        """Tag the text with Kkma and convert it into n-gram tokens.

        :param text: The input text or list of sentences
        :return: A list of n-gram tokens
        :raises TypeError: If the input is neither a string nor a list of strings
        """
        tokens: list[str] = []
        if isinstance(text, list):
            for t in text:
                tokens += self.morpheme(t)
        elif isinstance(text, str):
            tokens = self.morpheme(text)
        else:
            raise TypeError(  # noqa: TRY003
                "The dataset has to be string or list of string type."
            )

        return self.ngramize(tokens)

    def ngramize(self, tokens: list[str]) -> list[str]:
        """Generate n-grams of the tokens, dropping skip tags and out-of-vocabulary n-grams.

        :param tokens: A list of "surface/tag" tokens
        :return: A list of n-gram tokens joined by the delimiter
        """
        ngram_tokens: list[str] = []
        tokens = [w for w in tokens if w.split("/")[1] not in self._skiptags]
        for pos in range(len(tokens)):
            for gram in range(1, self._ngram + 1):
                if (token := self.get_ngram(tokens, pos, gram)) and (
                    (self._vocab is not None and token in self._vocab)
                    or self._vocab is None
                ):
                    ngram_tokens.append(token)
        return ngram_tokens

    def get_ngram(self, tokens: list[str], pos: int, gram: int) -> Optional[str]:
        """Return the n-gram of the given length starting at the given position.

        :param tokens: A list of tokens
        :param pos: The starting position of the n-gram
        :param gram: The length of the n-gram
        :return: The n-gram token joined by the delimiter, or None if out of range
        """
        if pos < 0:
            return None
        if pos + gram > len(tokens):
            return None
        token = tokens[pos]
        for i in range(1, gram):
            token += self._delimiter + tokens[pos + i]
        return token

    def morpheme(self, dataset: str) -> list[str]:
        """Tag the text with Kkma and return aligned morphemes.

        :param dataset: The input text to tag
        :return: A list of "surface/tag" strings
        """
        return self.align_morpheme(self._tagger.pos(dataset))

    def align_morpheme(self, morpheme: list[tuple[str, str]]) -> list[str]:
        """Convert (surface, tag) tuples into "surface/tag" strings.

        :param morpheme: A list of (surface, tag) tuples
        :return: A list of "surface/tag" strings
        """
        return [f"{w}/{t}" for w, t in morpheme]


class _TokenizerFiles(TypedDict):
    wordset: list[str]
    vocab: str


class MPTokenizer(BaseTokenizer):
    """
    The default tokenizer for MPKO sub class, which yields 5-gram tokens.
    The output of the tokenizer is tagged by Mecab.
    """

    KINDS: ClassVar[dict[int, int]] = {0: 5, 1: 5, 3: 3, 7: 7, 99: 1}
    FILES: ClassVar[_TokenizerFiles] = {
        "wordset": ["mpko/mp_polarity_wordset.txt"],
        "vocab": "mpko/mp_polarity_vocab.txt",
    }

    def __init__(
        self,
        kind: Optional[int] = None,
        vocab: Optional[Mapping[str, object]] = None,
        keep_overlapping_ngram: bool = False,
    ):
        """Initialize the tokenizer with the Mecab tagger, vocabulary, and word set.

        :param kind: A parameter to select the n-gram length; defaults to 0 (5-gram)
        :param vocab: A vocabulary mapping; the default vocabulary file is loaded if None
        :param keep_overlapping_ngram: Whether to keep n-grams that overlap longer n-grams
        """
        self._kind = kind if kind is not None and kind in self.KINDS else 0
        self._keep_overlapping_ngram = keep_overlapping_ngram
        self._min_ngram = 1
        self._delimiter = ";"
        self._ngram = self.KINDS[self._kind]
        self._tagger = Mecab()
        self._vocab: Mapping[str, object] = vocab or self.get_vocab(self.FILES["vocab"])
        self._wordset = self.get_wordset(self.FILES["wordset"])
        self._start_tags = {"NNG", "VA", "VAX", "MAG"}
        self._noun_tags = {"NNG"}

    def tokenize(self, text: Union[str, list[str]]) -> list[str]:
        """Tag the text with Mecab and convert it into n-gram tokens.

        :param text: The input text or list of sentences
        :return: A list of n-gram tokens
        """
        if isinstance(text, list):
            ngram_tokens: list[str] = []
            for t in text:
                tokens = self._tagger.sent_words(t)
                ngram_tokens += self.ngramize(tokens)
        else:
            tokens = self._tagger.sent_words(text)
            ngram_tokens = self.ngramize(tokens)
        return ngram_tokens

    def ngramize(self, tokens: list[str]) -> list[str]:
        """Generate n-grams of the tokens, keeping only in-vocabulary ones.

        Overlapping n-grams are dropped unless the tokenizer was created with
        `keep_overlapping_ngram=True`.

        :param tokens: A list of "surface/tag" tokens
        :return: A list of n-gram tokens joined by the delimiter
        """
        ngram_tokens: list[str] = []
        tokens = [w for w in tokens if w in self._wordset]

        for pos in range(len(tokens)):
            for gram in range(self._min_ngram, self._ngram + 1):
                if (token := self.get_ngram(tokens, pos, gram)) and (
                    (not self._keep_overlapping_ngram and token in self._vocab)
                    or self._keep_overlapping_ngram
                ):
                    ngram_tokens.append(token)
        if not self._keep_overlapping_ngram:
            filtered_tokens: list[str] = []
            if ngram_tokens:
                ngram_tokens = sorted(
                    ngram_tokens, key=lambda item: len(item), reverse=True
                )
                for token in ngram_tokens:
                    existing_token = any(
                        token in check_token for check_token in filtered_tokens
                    )
                    if not existing_token:
                        filtered_tokens.append(token)
            ngram_tokens = filtered_tokens

        return ngram_tokens

    def get_phrase(self, ngram_tokens: str) -> str:
        """Render an n-gram token as a phrase by concatenating its surfaces.

        :param ngram_tokens: The n-gram token to render
        :return: The phrase string
        """
        tokens = ngram_tokens.split(self._delimiter)
        phrase = ""
        for token in tokens:
            w, _t = token.split("/")
            phrase += w
        return phrase

    def get_ngram(self, tokens: list[str], pos: int, gram: int) -> Optional[str]:
        """Return the n-gram starting at the given position if it forms a valid phrase.

        The n-gram must start with an allowed tag, contain a noun, and have no repeated
        adjacent tokens.

        :param tokens: A list of "surface/tag" tokens
        :param pos: The starting position of the n-gram
        :param gram: The length of the n-gram
        :return: The n-gram token joined by the delimiter, or None if invalid or out of range
        """
        if pos < 0:
            return None
        if pos + gram > len(tokens):
            return None
        token = tokens[pos]
        check_noun = False

        tag = token.split("/")[1] if "/" in token else None
        if tag not in self._start_tags:
            return None
        if tag in self._noun_tags:
            check_noun = True
        for i in range(1, gram):
            if tokens[pos + i] != tokens[pos + i - 1]:
                tag = tokens[pos + i].split("/")[1] if "/" in tokens[pos + i] else None
                if tag in self._noun_tags:
                    check_noun = True
                token += self._delimiter + tokens[pos + i]
        return token if check_noun else None

    def get_wordset(self, files: list[str]) -> set[str]:
        """Load the word set used to filter tokens from the given lexicon files.

        :param files: Lexicon file paths relative to the lexicon directory
        :return: A set of words
        """
        wordset: set[str] = set()
        for file in files:
            with open(os.path.join(LEXICON_PATH, file), encoding="utf-8") as fin:
                for line in fin:
                    if not line.strip():
                        continue
                    word = line.strip().split()[0]
                    if len(word) > 1:
                        wordset.add(word)
        return wordset

    def get_vocab(self, file: str) -> dict[str, str]:
        """Load the n-gram vocabulary from the given lexicon file.

        :param file: A lexicon file path relative to the lexicon directory
        :return: A dictionary mapping n-grams to their values
        :raises ValueError: If a vocabulary entry is malformed
        """
        vocab: dict[str, str] = {}
        vocab_path = os.path.join(LEXICON_PATH, file)
        with open(vocab_path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                fields = line.split()
                if len(fields) < 2:
                    raise ValueError(  # noqa: TRY003
                        f"Malformed vocabulary entry at {vocab_path}:{line_number}"
                    )
                vocab[fields[0]] = fields[1]
        return vocab


class Tokenizer(BaseTokenizer):
    """
    The default tokenizer, which only takes care of words made up of ``[a-z]+``.
    The output of the tokenizer is stemmed by ``nltk.PorterStemmer``.

    The stoplist from https://www3.nd.edu/~mcdonald/Word_Lists.html is included in this
    tokenizer. Any word in the stoplist will be excluded from the output.
    """

    def __init__(self) -> None:
        """Initialize the tokenizer with the Porter stemmer and the stoplist."""
        self._stemmer = nltk.PorterStemmer()
        self._stopset = self.get_stopset()

    def tokenize(self, text: str) -> list[str]:
        """Tokenize the text into stemmed lowercase words, excluding stopwords.

        :param text: The input text to tokenize
        :return: A list of stemmed tokens
        """
        tokens: list[str] = []
        for t in nltk.regexp_tokenize(text.lower(), "[a-z]+"):
            t = self._stemmer.stem(t)
            if t not in self._stopset:
                tokens.append(t)
        return tokens

    # def ngramize(self, tokens):
    #     return tokens

    def get_stopset(self) -> set[str]:
        """Load and stem the stopwords from the Loughran-McDonald stoplist files.

        :return: A set of stemmed stopwords
        """
        files = [
            "Currencies.txt",
            "DatesandNumbers.txt",
            "Generic.txt",
            "Geographic.txt",
            "Names.txt",
        ]
        stopset = set()
        for f in files:
            with open(f"{LEXICON_PATH}/{f}", "rb") as fin:
                for raw_line in fin:
                    line = raw_line.decode(encoding="latin-1")
                    match = re.search(r"(\w+)", line)
                    if match is None:
                        continue
                    word = match[1]
                    stopset.add(self._stemmer.stem(word.lower()))
        return stopset


def calc_polarity(scores: Sequence[float], by_count: bool = True) -> float:
    """Calculate the polarity of a sequence of sentiment scores.

    :param scores: A sequence of sentiment scores
    :param by_count: If True, count occurrences of positive/negative scores instead of summing them
    :return: The polarity score in [-1, 1]
    """
    eps = 1e-6
    pos_score: list[float]
    neg_score: list[float]
    if by_count:
        pos_score = [1 for s in scores if s > 0]
        neg_score = [-1 for s in scores if s < 0]
    else:
        pos_score = [s for s in scores if s > 0]
        neg_score = [s for s in scores if s < 0]

    s_pos = sum(pos_score)
    s_neg = sum(neg_score)

    return (
        (s_pos + s_neg)
        * 1.0
        / (((s_pos - s_neg) if by_count else (len(pos_score) + len(neg_score))) + eps)
    )
