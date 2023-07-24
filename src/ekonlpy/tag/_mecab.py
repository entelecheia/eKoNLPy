import os
from typing import Dict, List, Optional, Set, Tuple, Union

from ekonlpy.data.tagset import lemma_tags
from ekonlpy.data.tagset import mecab_tags as tagset
from ekonlpy.data.tagset import mecab_tags_en as tagset_en
from ekonlpy.data.tagset import nouns_tags, sent_tags, stop_tags, topic_tags
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
    use_default_dictionary: bool = True
    use_polarity_phrase: bool = False
    use_original_tagger: bool = False
    tagset: Dict[str, str] = tagset
    tagset_en: Dict[str, str] = tagset_en
    stopwords: List[str] = []

    _term_tags: Dict[str, str] = term_tags
    _nouns_tags: Set[str] = nouns_tags
    _topic_tags: Set[str] = topic_tags
    _stop_tags: Set[str] = stop_tags
    _sent_tags: Set[str] = sent_tags
    _lemma_tags: Set[str] = lemma_tags
    _synonyms: Dict[str, str] = {}
    _lemmas: Dict[str, str] = {}
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
        **kwargs,
    ):
        super().__init__(dicdir, userdic_path, verbose, **kwargs)
        self.use_default_dictionary = use_default_dictionary
        self.use_polarity_phras = use_polarity_phrase
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

    def _load_stopwords(self) -> List[str]:
        directory = os.path.join(installpath, "data", "dictionary")
        return load_txt(os.path.join(directory, "STOPWORDS.txt"))

    def _load_synonyms(self, use_polarity_phrases: bool):
        directory = os.path.join(installpath, "data", "dictionary")
        self.load_synonyms(os.path.join(directory, "SYNONYM.txt"))
        self.load_synonyms(os.path.join(directory, "SYNONYM_MAG.txt"), tag="MAG")
        self.load_synonyms(os.path.join(directory, "SYNONYM_VA.txt"), tag="VAX")
        if use_polarity_phrases:
            self.load_synonyms(os.path.join(directory, "SYNONYM_PHRASES.txt"))

    def _load_lemmas(self):
        directory = os.path.join(installpath, "data", "dictionary")
        self.load_lemmas(os.path.join(directory, "LEMMA.txt"))

    def _load_default_dictionary(self, use_polarity_phrases):
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

    def _load_term_dictionary(self):
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
    ) -> List[Tuple[str, str]]:
        tagged = super().parse(text, flatten, include_whitespace_token)
        return self._extagger.pos(tagged) if self._extagger else tagged

    def pos(
        self,
        text: str,
        flatten: bool = True,
        include_whitespace_token: bool = False,
    ) -> List[Tuple[str, str]]:
        return self.parse(text, flatten, include_whitespace_token)

    def nouns(
        self,
        text: Union[str, List[Tuple[str, str]]],
        replace_synonym: bool = True,
        include_industry_terms: bool = False,
        include_generic: bool = False,
        include_sector_name: bool = False,
        include_country_name: bool = True,
        flatten: bool = True,
        noun_pos: Optional[List[str]] = None,
    ) -> List[str]:
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
        self, phrase: Union[str, List[Tuple[str, str]]]
    ) -> List[Tuple[str, str]]:
        tagged = self.pos(phrase) if isinstance(phrase, str) else phrase
        replaced = []
        for w, t in tagged:
            if w.lower() in self._synonyms:
                replaced.append((self._synonyms[w.lower()].lower(), t))
            else:
                replaced.append((w, t))
        return replaced

    def lemmatize(self, phrase: Union[str, List[Tuple[str, str]]]) -> List[str]:
        tagged = self.pos(phrase) if isinstance(phrase, str) else phrase
        replaced = []
        for w, t in tagged:
            if t in self._lemma_tags and w.lower() in self._lemmas:
                t = "VV" if t == "XSV" else t
                replaced.append((self._lemmas[w.lower()], t))
            else:
                replaced.append((w, t))
        return replaced

    def sent_words(
        self,
        phrase: Union[str, List[Tuple[str, str]]],
        replace_synonym: bool = True,
        lemmatisation: bool = True,
        exclude_terms: bool = True,
        remove_tag: bool = False,
    ) -> List[str]:
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

    def morphs(self, text: str, flatten: bool = True) -> List[str]:
        tagged = self.pos(text, flatten=flatten) if isinstance(text, str) else text
        return [s for s, t in tagged]

    # def phrases(self, phrase):
    #     return self._base.phrases(phrase)

    def add_dictionary(
        self,
        words: Union[str, List[str]],
        tag: str,
        force: bool = False,
    ) -> None:
        if not force and tag not in self.tagset:
            raise ValueError(f"{tag} is not available tag")
        self._dictionary.add_dictionary(words, tag)

    def load_dictionary(
        self,
        fname: str,
        tag: str,
    ) -> None:
        if tag not in self.tagset:
            raise ValueError(f"{tag} is not available tag")
        self._dictionary.load_dictionary(fname, tag)

    def add_terms(
        self,
        words: List[str],
        tag: str,
        force: bool = False,
    ) -> None:
        """
        Add words to the dictionary with the given tag. If force is
        set, tags not in the dictionary will be added.
        """
        if not force and tag not in self._term_tags:
            raise ValueError(f"{tag} is not available tag")
        self._dictionary.add_dictionary(words, tag)

    def load_terms(
        self,
        fname: str,
        tag: str,
    ) -> None:
        if tag not in self._term_tags:
            raise ValueError(f"{tag} is not available tag")
        self._dictionary.load_dictionary(fname, tag)

    def load_synonyms(
        self,
        fname: str,
        tag: str = "NNG",
    ) -> None:
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
        self._synonyms[word.lower()] = synonym.lower()
        self.add_dictionary(word, tag)
        self.add_dictionary(synonym, tag)

    def persist_synonyms(self) -> None:
        directory = os.path.join(installpath, "data", "dictionary")
        return save_vocab(self._synonyms, os.path.join(directory, "SYNONYM.txt"))

    def load_lemmas(self, fname: str) -> None:
        vocab = load_vocab(fname)
        self._lemmas.update(vocab)

    def add_lemma(self, word: str, lemma: str) -> None:
        self._lemmas[word] = lemma

    def persist_lemmas(self) -> None:
        directory = os.path.join(installpath, "data", "dictionary")
        return save_vocab(self._lemmas, os.path.join(directory, "LEMMA.txt"))


if __name__ == "__main__":
    tagger = Mecab()
    text = "아버지가 방에 들어가신다."
    print(tagger._parse(text))
    print(tagger.pos(text))
    print(tagger.morphs(text))
    print(tagger.nouns(text))
