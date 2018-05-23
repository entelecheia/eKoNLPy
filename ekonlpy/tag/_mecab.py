from konlpy.tag import Mecab as KoNLPyMecab
from ekonlpy.etag import ExTagger
from ekonlpy.data.tagset import mecab_tags as tagset
from ekonlpy.data.tagset import nouns_tags, stop_tags, sent_tags, topic_tags
from ekonlpy.dictionary import TermDictionary, term_tags
from ekonlpy.utils import installpath
from ekonlpy.utils import load_dictionary, loadtxt, load_vocab, save_vocab


class Mecab:
    def __init__(self, use_default_dictionary=True,
                 use_phrases=True, use_polarity_phrases=True,
                 replace_synonyms=True, combine_suffixes=True):
        self._base = KoNLPyMecab()
        self._dictionary = TermDictionary()
        self._terms = TermDictionary()
        self.use_default_dictionary = use_default_dictionary
        self.use_phrases = use_phrases
        self.use_polarity_phrases = use_polarity_phrases
        self.replace_synonyms = replace_synonyms
        self.combine_suffixes = combine_suffixes
        if use_default_dictionary:
            self._load_default_dictionary(use_phrases, use_polarity_phrases)
        self._load_term_dictionary()
        self.extagger = self._load_ext_tagger()
        self.tagset = tagset
        self.term_tags = term_tags
        self.nouns_tags = nouns_tags
        self.topic_tags = topic_tags
        self.stop_tags = stop_tags
        self.sent_tags = sent_tags
        self.stopwords = self._load_stopwords()
        self.synonyms = {}
        self._load_synonyms(use_polarity_phrases)

    def _load_ext_tagger(self):
        return ExTagger(self._dictionary)

    def _load_stopwords(self):
        directory = '%s/data/dictionary/' % installpath
        return loadtxt('%s/STOPWORDS.txt' % directory)

    def _load_synonyms(self, use_polarity_phrases):
        directory = '%s/data/dictionary/' % installpath
        self.load_synonyms('%s/SYNONYM.txt' % directory)
        if use_polarity_phrases:
            self.load_synonyms('%s/SYNONYM_PHRASES.txt' % directory)

    def _load_default_dictionary(self, use_phrases, use_polarity_phrases):
        directory = '%s/data/dictionary/' % installpath
        self._dictionary.add_dictionary(load_dictionary('%s/ECON_TERMS.txt' % directory), 'NNG')
        self._dictionary.add_dictionary(load_dictionary('%s/INDUSTRY_TERMS.txt' % directory), 'NNG')
        self._dictionary.add_dictionary(load_dictionary('%s/COUNTRY.txt' % directory), 'NNG')
        self._dictionary.add_dictionary(load_dictionary('%s/PROPER_NOUNS.txt' % directory), 'NNP')
        self._dictionary.add_dictionary(load_dictionary('%s/ENTITY.txt' % directory), 'NNP')
        self._dictionary.add_dictionary(load_dictionary('%s/INSTITUTION.txt' % directory), 'NNP')
        self._dictionary.add_dictionary(load_dictionary('%s/ADJECTIVES.txt' % directory), 'VA')
        self._dictionary.add_dictionary(load_dictionary('%s/ADVERBES.txt' % directory), 'MAG')
        self._dictionary.add_dictionary(load_dictionary('%s/FOREIGN_TERMS.txt' % directory), 'SL')
        if use_phrases:
            self._dictionary.add_dictionary(load_dictionary('%s/ECON_PHRASES.txt' % directory), 'NNG')
            self._dictionary.add_dictionary(load_dictionary('%s/SECTOR.txt' % directory), 'NNP')
        if use_polarity_phrases:
            self._dictionary.add_dictionary(load_dictionary('%s/POLARITY_PHRASES.txt' % directory), 'NNG')

    def _load_term_dictionary(self):
        directory = '%s/data/dictionary/' % installpath
        self._terms.add_dictionary(load_dictionary('%s/COUNTRY.txt' % directory), 'COUNTRY')
        # self._terms.add_dictionary(load_dictionary('%s/SECTOR.txt' % directory), 'SECTOR')
        self._terms.add_dictionary(load_dictionary('%s/INDUSTRY_TERMS.txt' % directory), 'INDUSTRY')

    def pos(self, phrase):
        tagged = self._base.pos(phrase)
        tagged = self.extagger.pos(tagged, combine_suffixes=self.combine_suffixes)
        if self.replace_synonyms:
            tagged = [(self.synonyms[w.lower()] if w.lower() in self.synonyms else w, t)
                      for w, t in tagged]

        return tagged

    def nouns(self, phrase, exclude_industry_terms=True):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        if exclude_industry_terms:
            return [w.lower() for w, t in tagged
                    if t in self.topic_tags and w.lower()
                    and not self._terms.exists(w, 'INDUSTRY')]
        else:
            return [w.lower() for w, t in tagged if t in self.topic_tags and w.lower()]

    def sent_words(self, phrase, exclude_terms=True):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        if exclude_terms:
            return ['{}/{}'.format(w.lower(), t.split('+')[0])
                    for w, t in tagged
                    if t in self.sent_tags
                    and not self._terms.exists(w)]
        else:
            return ['{}/{}'.format(w.lower(), t.split('+')[0]) for w, t in tagged
                    if t in self.sent_tags and w.lower()]

    def morphs(self, phrase):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        return [s for s, t in tagged]

    def phrases(self, phrase):
        return self._base.phrases(phrase)

    def add_dictionary(self, words, tag, force=False):
        if (not force) and (not (tag in self.tagset)):
            raise ValueError('%s is not available tag' % tag)
        self._dictionary.add_dictionary(words, tag)

    def load_dictionary(self, fname, tag):
        if not (tag in self.tagset):
            raise ValueError('%s is not available tag' % tag)
        self._dictionary.load_dictionary(fname, tag)

    def add_terms(self, words, tag, force=False):
        if (not force) and (not (tag in self.term_tags)):
            raise ValueError('%s is not available tag' % tag)
        self._dictionary.add_dictionary(words, tag)

    def load_terms(self, fname, tag):
        if not (tag in self.term_tags):
            raise ValueError('%s is not available tag' % tag)
        self._dictionary.load_dictionary(fname, tag)

    def load_synonyms(self, fname):
        vocab = load_vocab(fname)
        self.add_dictionary(vocab.keys(), 'NNG')
        self.add_dictionary(vocab.values(), 'NNG')
        self.synonyms.update(vocab)

    def add_synonym(self, word, synonym):
        self.synonyms[word] = synonym
        self.add_dictionary(word, 'NNG')
        self.add_dictionary(synonym, 'NNG')

    def persist_synonyms(self):
        directory = '%s/data/dictionary/' % installpath
        return save_vocab(self.synonyms, '%s/SYNONYM.txt' % directory)
