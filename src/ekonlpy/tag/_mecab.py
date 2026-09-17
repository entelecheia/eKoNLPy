import os
from typing import Optional, Union

from ekonlpy.data.tagset import (
    lemma_tags,
    mecab_tags,
    mecab_tags_en,
    nouns_tags,
    sent_tags,
    stop_tags,
    topic_tags,
)
from ekonlpy.etag import ExtTagger
from ekonlpy.mecab import Mecab as FugashiMecab
from ekonlpy.utils.dictionary import TermDictionary, term_tags
from ekonlpy.utils.io import (
    installpath,
    load_dictionary,
    load_txt,
    load_vocab,
    save_vocab,
)


class Mecab(FugashiMecab):
    """The extended MeCab tagger for economic text, with custom dictionaries and an n-gram tagger."""

    use_default_dictionary: bool = True
    use_polarity_phrase: bool = False
    use_original_tagger: bool = False
    tagset: dict[str, str] = mecab_tags
    tagset_en: dict[str, str] = mecab_tags_en
    stopwords: list[str]

    _term_tags: dict[str, str] = term_tags
    _nouns_tags: set[str] = nouns_tags
    _topic_tags: set[str] = topic_tags
    _stop_tags: set[str] = stop_tags
    _sent_tags: set[str] = sent_tags
    _lemma_tags: set[str] = lemma_tags
    _synonyms: dict[str, str]
    _lemmas: dict[str, str]
    _dictionary: TermDictionary = TermDictionary()
    _terms: TermDictionary = TermDictionary()
    _extagger: Optional[ExtTagger] = None

    def __init__(
        self,
        use_default_dictionary: bool = True,
        use_polarity_phrase: bool = False,
        use_original_tagger: bool = False,
        dicdir: Optional[str] = None,
        userdic_path: Optional[str] = None,
        verbose: bool = False,
        **kwargs: object,
    ):
        """Initialize the extended tagger and load the dictionaries, synonyms, and lemmas.

        :param use_default_dictionary: Whether to load the default eKoNLPy dictionaries
        :param use_polarity_phrase: Whether to include polarity phrases in the dictionaries
        :param use_original_tagger: Whether to use the original MeCab tagger without extensions
        :param dicdir: Path to the system dictionary directory; defaults to the mecab-ko-dic path
        :param userdic_path: Path to a compiled user dictionary, if any
        :param verbose: Whether to log detailed loading information
        :param kwargs: Additional keyword arguments passed to the base tagger
        """
        super().__init__(dicdir, userdic_path, verbose, **kwargs)
        self.tagset = dict(type(self).tagset)
        self.tagset_en = dict(type(self).tagset_en)
        self._term_tags = dict(type(self)._term_tags)
        self._nouns_tags = set(type(self)._nouns_tags)
        self._topic_tags = set(type(self)._topic_tags)
        self._stop_tags = set(type(self)._stop_tags)
        self._sent_tags = set(type(self)._sent_tags)
        self._lemma_tags = set(type(self)._lemma_tags)
        self._synonyms = {}
        self._lemmas = {}
        self._dictionary = TermDictionary()
        self._terms = TermDictionary()
        self._extagger = None
        self.stopwords = []
        self.use_default_dictionary = use_default_dictionary
        self.use_polarity_phrase = use_polarity_phrase
        self.use_original_tagger = use_original_tagger
        if use_original_tagger:
            return

        if use_default_dictionary:
            self._load_default_dictionary(use_polarity_phrase)
        self._load_term_dictionary()
        self._extagger = self._load_ext_tagger()
        self.stopwords = self._load_stopwords()
        self._load_synonyms(use_polarity_phrase)
        self._load_lemmas()

    def _load_ext_tagger(self) -> ExtTagger:
        return ExtTagger(self._dictionary)

    def _load_stopwords(self) -> list[str]:
        directory = os.path.join(installpath, "data", "dictionary")
        return load_txt(os.path.join(directory, "STOPWORDS.txt"))

    def _load_synonyms(self, use_polarity_phrases: bool) -> None:
        directory = os.path.join(installpath, "data", "dictionary")
        self.load_synonyms(os.path.join(directory, "SYNONYM.txt"))
        self.load_synonyms(os.path.join(directory, "SYNONYM_MAG.txt"), tag="MAG")
        self.load_synonyms(os.path.join(directory, "SYNONYM_VA.txt"), tag="VAX")
        if use_polarity_phrases:
            self.load_synonyms(os.path.join(directory, "SYNONYM_PHRASES.txt"))

    def _load_lemmas(self) -> None:
        directory = os.path.join(installpath, "data", "dictionary")
        self.load_lemmas(os.path.join(directory, "LEMMA.txt"))

    def _load_default_dictionary(self, use_polarity_phrases: bool) -> None:
        directory = os.path.join(installpath, "data", "dictionary")
        # self._dictionary.add_dictionary(load_dictionary(os.path.join(directory, 'GENERIC.txt')), 'NNG')
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "NOUNS.txt")), "NNG"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "NAMES.txt")), "NNG"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "ECON_TERMS.txt")), "NNG"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "INDUSTRY_TERMS.txt")), "NNG"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "COUNTRY.txt")), "NNG"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "PROPER_NOUNS.txt")), "NNP"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "ENTITY.txt")), "NNP"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "INSTITUTION.txt")), "NNP"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "ADJECTIVES.txt")), "VAX"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "ADVERBS.txt")), "MAG"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "VERBS.txt")), "VV"
        )
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "UNIT.txt")), "NNBC"
        )
        # self._dictionary.add_dictionary(load_dictionary(os.path.join(directory, 'FOREIGN_TERMS.txt')), 'SL')
        # self._dictionary.add_dictionary(load_dictionary(os.path.join(directory, 'ECON_PHRASES.txt')), 'NNG')
        self._dictionary.add_dictionary(
            load_dictionary(os.path.join(directory, "SECTOR.txt")), "NNG"
        )
        if use_polarity_phrases:
            self._dictionary.add_dictionary(
                load_dictionary(os.path.join(directory, "POLARITY_PHRASES.txt")), "NNG"
            )

    def _load_term_dictionary(self) -> None:
        directory = os.path.join(installpath, "data", "dictionary")
        self._terms.add_dictionary(
            load_dictionary(os.path.join(directory, "COUNTRY.txt")), "COUNTRY"
        )
        self._terms.add_dictionary(
            load_dictionary(os.path.join(directory, "SECTOR.txt")), "SECTOR"
        )
        self._terms.add_dictionary(
            load_dictionary(os.path.join(directory, "INDUSTRY_TERMS.txt")), "INDUSTRY"
        )
        self._terms.add_dictionary(
            load_dictionary(os.path.join(directory, "GENERIC.txt")), "GENERIC"
        )
        self._terms.add_dictionary(
            load_dictionary(os.path.join(directory, "CURRENCY.txt")), "CURRENCY"
        )
        self._terms.add_dictionary(
            load_dictionary(os.path.join(directory, "UNIT.txt")), "UNIT"
        )
        self._terms.add_dictionary(
            load_dictionary(os.path.join(directory, "NAMES.txt")), "NAME"
        )

    def parse(
        self,
        text: str,
        flatten: bool = True,
        include_whitespace_token: bool = False,
    ) -> list[tuple[str, str]]:
        """Tag text and merge token n-grams into dictionary terms with the extended tagger.

        :param text: The input text to tag
        :param flatten: Whether to decompose inflected expressions into their morphemes
        :param include_whitespace_token: Whether to preserve whitespace runs as SP tokens
        :return: A list of (surface, pos) tuples
        """
        tagged = super().parse(text, flatten, include_whitespace_token)
        return self._extagger.pos(tagged) if self._extagger else tagged

    def pos(
        self,
        text: str,
        flatten: bool = True,
        include_whitespace_token: bool = False,
    ) -> list[tuple[str, str]]:
        """Return POS-tagged tokens for the given text.

        :param text: The input text to tag
        :param flatten: Whether to decompose inflected expressions into their morphemes
        :param include_whitespace_token: Whether to preserve whitespace runs as SP tokens
        :return: A list of (surface, pos) tuples
        """
        return self.parse(text, flatten, include_whitespace_token)

    def nouns(  # type: ignore[override]
        self,
        text: Union[str, list[tuple[str, str]]],
        replace_synonym: bool = True,
        include_industry_terms: bool = False,
        include_generic: bool = False,
        include_sector_name: bool = False,
        include_country_name: bool = True,
        flatten: bool = True,
        noun_pos: Optional[list[str]] = None,
    ) -> list[str]:
        """Return the topical nouns of the given text or pre-tagged tokens.

        :param text: The input text, or a list of (surface, pos) tuples already tagged
        :param replace_synonym: Whether to replace synonyms with their canonical forms
        :param include_industry_terms: Whether to keep industry terms
        :param include_generic: Whether to keep generic terms
        :param include_sector_name: Whether to keep sector names
        :param include_country_name: Whether to keep country names
        :param flatten: Whether to decompose inflected expressions into their morphemes
        :param noun_pos: POS tags considered as nouns; defaults to common noun tags
        :return: A list of lowercased noun surfaces
        """
        if self.use_original_tagger:
            return super().nouns(text, flatten=flatten, noun_pos=noun_pos)
        tagged = self.pos(text, flatten=flatten) if isinstance(text, str) else text
        if replace_synonym:
            tagged = self.replace_synonyms(tagged)
        return [
            w.lower()
            for w, t in tagged
            if t in self._topic_tags
            and (include_industry_terms or not self._terms.exists(w, "INDUSTRY"))
            and (include_generic or not self._terms.exists(w, "GENERIC"))
            and (include_sector_name or not self._terms.exists(w, "SECTOR"))
            and (include_country_name or not self._terms.exists(w, "COUNTRY"))
        ]

    def replace_synonyms(
        self, phrase: Union[str, list[tuple[str, str]]]
    ) -> list[tuple[str, str]]:
        """Replace words with their canonical synonyms.

        :param phrase: The input text, or a list of (surface, pos) tuples already tagged
        :return: The tagged tokens with synonyms replaced
        """
        tagged = self.pos(phrase) if isinstance(phrase, str) else phrase
        replaced: list[tuple[str, str]] = []
        for w, t in tagged:
            if w.lower() in self._synonyms:
                replaced.append((self._synonyms[w.lower()].lower(), t))
            else:
                replaced.append((w, t))
        return replaced

    def lemmatize(
        self, phrase: Union[str, list[tuple[str, str]]]
    ) -> list[tuple[str, str]]:
        """Replace inflected words with their lemmas.

        :param phrase: The input text, or a list of (surface, pos) tuples already tagged
        :return: The tagged tokens with lemmas applied
        """
        tagged = self.pos(phrase) if isinstance(phrase, str) else phrase
        replaced: list[tuple[str, str]] = []
        for w, t in tagged:
            if t in self._lemma_tags and w.lower() in self._lemmas:
                t = "VV" if t == "XSV" else t
                replaced.append((self._lemmas[w.lower()], t))
            else:
                replaced.append((w, t))
        return replaced

    def sent_words(
        self,
        phrase: Union[str, list[tuple[str, str]]],
        replace_synonym: bool = True,
        lemmatisation: bool = True,
        exclude_terms: bool = True,
        remove_tag: bool = False,
    ) -> list[str]:
        """Return sentiment-bearing words of the given text or pre-tagged tokens.

        Synonyms are replaced and words are lemmatized by default, and only words with
        sentiment tags are kept.

        :param phrase: The input text, or a list of (surface, pos) tuples already tagged
        :param replace_synonym: Whether to replace synonyms with their canonical forms
        :param lemmatisation: Whether to lemmatize the words
        :param exclude_terms: Whether to exclude dictionary terms from the output
        :param remove_tag: Whether to drop the POS tags from the output
        :return: A list of "word/tag" strings, or bare words if remove_tag is True
        """
        tagged = self.pos(phrase) if isinstance(phrase, str) else phrase
        if replace_synonym:
            tagged = self.replace_synonyms(tagged)
        if lemmatisation:
            tagged = self.lemmatize(tagged)
        if exclude_terms:
            return [
                w.lower() if remove_tag else f'{w.lower()}/{t.split("+")[0]}'
                for w, t in tagged
                if t in self._sent_tags and not self._terms.exists(w)
            ]
        else:
            return [
                w.lower() if remove_tag else f'{w.lower()}/{t.split("+")[0]}'
                for w, t in tagged
                if t in self._sent_tags
            ]

    def morphs(self, text: str, flatten: bool = True) -> list[str]:
        """Return the morphemes (surfaces without POS tags) of the given text.

        :param text: The input text to analyze
        :param flatten: Whether to decompose inflected expressions into their morphemes
        :return: A list of morpheme strings
        """
        tagged = self.pos(text, flatten=flatten) if isinstance(text, str) else text
        return [s for s, t in tagged]

    # def phrases(self, phrase):
    #     return self._base.phrases(phrase)

    def add_dictionary(
        self,
        words: Union[str, list[str]],
        tag: str,
        force: bool = False,
    ) -> None:
        """Add words to the tagging dictionary under the given POS tag.

        :param words: A word or a list of words to add
        :param tag: The POS tag for the words
        :param force: Whether to allow tags not in the tagset
        :raises ValueError: If the tag is not in the tagset and force is False
        """
        if not force and tag not in self.tagset:
            raise ValueError(f"{tag} is not available tag")  # noqa: TRY003
        self._dictionary.add_dictionary(words, tag)

    def load_dictionary(
        self,
        fname: str,
        tag: str,
    ) -> None:
        """Load words from a file into the tagging dictionary under the given POS tag.

        :param fname: Path of the dictionary file to load
        :param tag: The POS tag for the loaded words
        :raises ValueError: If the tag is not in the tagset
        """
        if tag not in self.tagset:
            raise ValueError(f"{tag} is not available tag")  # noqa: TRY003
        self._dictionary.load_dictionary(fname, tag)

    def add_terms(
        self,
        words: list[str],
        tag: str,
        force: bool = False,
    ) -> None:
        """
        Add words to the dictionary with the given tag. If force is
        set, tags not in the dictionary will be added.
        """
        if not force and tag not in self._term_tags:
            raise ValueError(f"{tag} is not available tag")  # noqa: TRY003
        self._terms.add_dictionary(words, tag)

    def load_terms(
        self,
        fname: str,
        tag: str,
    ) -> None:
        """Load terms from a file into the term dictionary under the given tag.

        :param fname: Path of the term file to load
        :param tag: The term tag for the loaded words
        :raises ValueError: If the tag is not a valid term tag
        """
        if tag not in self._term_tags:
            raise ValueError(f"{tag} is not available tag")  # noqa: TRY003
        self._terms.load_dictionary(fname, tag)

    def load_synonyms(
        self,
        fname: str,
        tag: str = "NNG",
    ) -> None:
        """Load synonym pairs from a file and register them in the tagging dictionary.

        :param fname: Path of the synonym file to load
        :param tag: The POS tag for the synonyms
        """
        vocab = load_vocab(fname)
        self._synonyms.update(vocab)
        self.add_dictionary(list(vocab.keys()), tag)
        self.add_dictionary(list(vocab.values()), tag)

    def add_synonym(
        self,
        word: str,
        synonym: str,
        tag: str = "NNG",
    ) -> None:
        """Add a synonym pair and register both words in the tagging dictionary.

        :param word: The word to be replaced
        :param synonym: The canonical synonym of the word
        :param tag: The POS tag for both words
        """
        self._synonyms[word.lower()] = synonym.lower()
        self.add_dictionary(word, tag)
        self.add_dictionary(synonym, tag)

    def persist_synonyms(self) -> None:
        """Save the current synonyms to the default SYNONYM.txt file."""
        directory = os.path.join(installpath, "data", "dictionary")
        return save_vocab(self._synonyms, os.path.join(directory, "SYNONYM.txt"))

    def load_lemmas(self, fname: str) -> None:
        """Load lemma pairs from a file.

        :param fname: Path of the lemma file to load
        """
        vocab = load_vocab(fname)
        self._lemmas.update(vocab)

    def add_lemma(self, word: str, lemma: str) -> None:
        """Add a lemma pair.

        :param word: The inflected word
        :param lemma: The lemma of the word
        """
        self._lemmas[word] = lemma

    def persist_lemmas(self) -> None:
        """Save the current lemmas to the default LEMMA.txt file."""
        directory = os.path.join(installpath, "data", "dictionary")
        return save_vocab(self._lemmas, os.path.join(directory, "LEMMA.txt"))


if __name__ == "__main__":
    tagger = Mecab()
    text = "아버지가 방에 들어가신다."
    print(tagger._parse(text))
    print(tagger.pos(text))
    print(tagger.morphs(text))
    print(tagger.nouns(text))
