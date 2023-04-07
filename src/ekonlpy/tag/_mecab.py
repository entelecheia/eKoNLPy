import os
from typing import Dict, List, Tuple, Union

from ..data.tagset import lemma_tags
from ..data.tagset import mecab_tags as tagset
from ..data.tagset import mecab_tags_en as tagset_en
from ..data.tagset import nouns_tags, sent_tags, stop_tags, topic_tags
from ..etag import ExtTagger
from ..mecab import MeCab as _MeCab
from ..utils.dictionary import TermDictionary, term_tags
from ..utils.io import installpath, load_dictionary, load_txt, load_vocab, save_vocab


class Mecab:
    def __init__(
        self,
        use_default_dictionary: bool = True,
        use_polarity_phrase: bool = False,
    ):
        self._tokenizer = _MeCab()
        self._dictionary = TermDictionary()
        self._terms = TermDictionary()
        self.use_default_dictionary = use_default_dictionary
        self.use_polarity_phras = use_polarity_phrase
        if use_default_dictionary:
            self._load_default_dictionary(use_polarity_phrase)
        self._load_term_dictionary()
        self._extagger = self._load_ext_tagger()
        self.tagset = tagset
        self.tagset_en = tagset_en
        self._term_tags = term_tags
        self._nouns_tags = nouns_tags
        self._topic_tags = topic_tags
        self._stop_tags = stop_tags
        self._sent_tags = sent_tags
        self._lemma_tags = lemma_tags
        self.stopwords = self._load_stopwords()
        self._synonyms: Dict[str, str] = {}
        self._load_synonyms(use_polarity_phrase)
        self._lemmas: Dict[str, str] = {}
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

    def pos(self, phrase: str) -> List[Tuple[str, str]]:
        tagged = self._tokenizer.pos(phrase)
        tagged = self._extagger.pos(tagged)

        return tagged

    def nouns(
        self,
        phrase: Union[str, List[Tuple[str, str]]],
        replace_synonym: bool = True,
        include_industry_terms: bool = False,
        include_generic: bool = False,
        include_sector_name: bool = False,
        include_country_name: bool = True,
    ) -> List[str]:
        tagged = self.pos(phrase) if type(phrase) == str else phrase
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

    def replace_synonyms(self, phrase):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        replaced = []
        for w, t in tagged:
            if w.lower() in self._synonyms:
                replaced.append((self._synonyms[w.lower()].lower(), t))
            else:
                replaced.append((w, t))
        return replaced

    def lemmatize(self, phrase):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
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
        phrase,
        replace_synonym=True,
        lemmatisation=True,
        exclude_terms=True,
        remove_tag=False,
    ):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        if replace_synonym:
            tagged = self.replace_synonyms(tagged)
        if lemmatisation:
            tagged = self.lemmatize(tagged)
        if exclude_terms:
            return [
                "{}/{}".format(w.lower(), t.split("+")[0])
                if not remove_tag
                else w.lower()
                for w, t in tagged
                if t in self._sent_tags and not self._terms.exists(w)
            ]
        else:
            return [
                "{}/{}".format(w.lower(), t.split("+")[0])
                if not remove_tag
                else w.lower()
                for w, t in tagged
                if t in self._sent_tags
            ]

    def morphs(self, phrase):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        return [s for s, t in tagged]

    # def phrases(self, phrase):
    #     return self._base.phrases(phrase)

    def add_dictionary(self, words, tag, force=False):
        if (not force) and (not (tag in self.tagset)):
            raise ValueError("%s is not available tag" % tag)
        self._dictionary.add_dictionary(words, tag)

    def load_dictionary(self, fname: str, tag: str) -> None:
        if not (tag in self.tagset):
            raise ValueError("%s is not available tag" % tag)
        self._dictionary.load_dictionary(fname, tag)

    def add_terms(self, words: List[str], tag: str, force: bool = False):
        """
        Add words to the dictionary with the given tag. If force is
        set, tags not in the dictionary will be added.
        """
        if (not force) and (not (tag in self._term_tags)):
            raise ValueError("%s is not available tag" % tag)
        self._dictionary.add_dictionary(words, tag)

    def load_terms(self, fname, tag):
        if not (tag in self._term_tags):
            raise ValueError("%s is not available tag" % tag)
        self._dictionary.load_dictionary(fname, tag)

    def load_synonyms(self, fname, tag="NNG"):
        vocab = load_vocab(fname)
        self._synonyms.update(vocab)
        self.add_dictionary(vocab.keys(), tag)
        self.add_dictionary(vocab.values(), tag)

    def add_synonym(self, word, synonym, tag="NNG"):
        self._synonyms[word.lower()] = synonym.lower()
        self.add_dictionary(word, tag)
        self.add_dictionary(synonym, tag)

    def persist_synonyms(self):
        directory = os.path.join(installpath, "data", "dictionary")
        return save_vocab(self._synonyms, os.path.join(directory, "SYNONYM.txt"))

    def load_lemmas(self, fname):
        vocab = load_vocab(fname)
        self._lemmas.update(vocab)

    def add_lemma(self, word, lemma):
        self._lemmas[word] = lemma

    def persist_lemmas(self):
        directory = os.path.join(installpath, "data", "dictionary")
        return save_vocab(self._lemmas, os.path.join(directory, "LEMMA.txt"))
