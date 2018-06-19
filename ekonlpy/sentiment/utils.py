'''
This module contains methods to tokenize sentences.
'''
import abc
import re
import nltk
import os
from ekonlpy.tag import Mecab
from ekonlpy.sentiment.base import LEXICON_PATH


class BaseTokenizer(object):
    '''
    An abstract class for tokenize text.
    '''

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def tokenize(self, text):
        '''Return tokenized temrs.
        
        :type text: str
        
        :returns: list 
        '''
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


class MPTokenizer(BaseTokenizer):
    '''
    The default tokenizer for MPKO sub class, which yields 5-gram tokens.
    The output of the tokenizer is tagged by Mecab.
    '''
    KINDS = {0: 5,
             1: 5
             }
    FILES = {'stopwords': ['mpko/mp_polarity_stopwords.txt'],
             'vocab': 'mpko/mp_polarity_map.txt'
             }

    def __init__(self, kind=None):
        self._kind = kind if kind in self.KINDS.keys() else 0
        self._min_ngram = 1
        self._delimiter = ';'
        self._ngram = self.KINDS[self._kind]
        self._tagger = Mecab()
        self._vocab = self.get_vocab(self.FILES['vocab'])
        self._stopwords = self.get_wordset(self.FILES['stopwords'])
        self._start_tags = {'NNG', 'VA', 'VAX'}
        self._noun_tags = {'NNG'}

    def tokenize(self, text):
        if type(text) == list:
            ngram_tokens = []
            for t in text:
                tokens = self._tagger.sent_words(t)
                ngram_tokens += self.ngramize(tokens)
        else:
            tokens = self._tagger.sent_words(text)
            ngram_tokens = self.ngramize(tokens)
        return ngram_tokens

    def ngramize(self, tokens, keep_overlapping_ngram=False):
        ngram_tokens = []
        tokens = [w for w in tokens if w not in self._stopwords]
        for pos in range(len(tokens)):
            for gram in range(self._min_ngram, self._ngram + 1):
                token = self.get_ngram(tokens, pos, gram)
                if token:
                    if token in self._vocab:
                        ngram_tokens.append(token)
        if not keep_overlapping_ngram:
            filtered_tokens = []
            if len(ngram_tokens) > 0:
                ngram_tokens = sorted(ngram_tokens, key=lambda item: len(item), reverse=True)
                for token in ngram_tokens:
                    existing_token = False
                    for check_token in filtered_tokens:
                        if token in check_token:
                            existing_token = True
                            break
                    if not existing_token:
                        filtered_tokens.append(token)
            ngram_tokens = filtered_tokens

        return ngram_tokens

    def get_phrase(self, ngram_tokens):
        tokens = ngram_tokens.split(self._delimiter)
        phrase = ''
        for token in tokens:
            w, t = token.split('/')
            phrase += w
        return phrase

    def get_ngram(self, tokens, pos, gram):
        if pos < 0:
            return None
        if pos + gram > len(tokens):
            return None
        token = tokens[pos]
        check_noun = False

        tag = token.split('/')[1] if '/' in token else None
        if tag in self._start_tags:
            if tag in self._noun_tags:
                check_noun = True
            for i in range(1, gram):
                if tokens[pos + i] not in token:
                    tag = tokens[pos + i].split('/')[1] if '/' in tokens[pos + i] else None
                    if tag in self._noun_tags:
                        check_noun = True
                    token += self._delimiter + tokens[pos + i]
            if len(token.split(self._delimiter)) == gram and check_noun:
                return token
            else:
                return None
        else:
            return None

    def get_wordset(self, files):
        wordset = set()
        for f in files:
            fin = open('%s/%s' % (LEXICON_PATH, f), 'r', encoding='utf-8')
            for line in fin.readlines():
                word = line.strip().split()[0]
                if len(word) > 1:
                    wordset.add(word)
            fin.close()
        return wordset

    def get_vocab(self, file):
        vocab = {}
        vocab_path = os.path.join(LEXICON_PATH, file)
        with open(vocab_path) as f:
            for i, line in enumerate(f):
                w = line.strip().split()
                if len(w[0]) > 0:
                    vocab[w[0]] = w[1]
        return vocab


class MPTokenizerx(BaseTokenizer):
    '''
    The default tokenizer for MPKO sub class, which yields 5-gram tokens.
    The output of the tokenizer is tagged by Mecab.
    '''
    KINDS = {0: 5,
             1: 5
             }
    FILES = {'stopwords': ['mpkox/mp_sent_stopwords.txt'],
             'stopngrams': ['mpkox/mp_sent_stop5grams.txt'],
             'startwords': ['mpkox/mp_sent_startwords.txt'],
             'vocab': 'mpkox/mp_sent_vocab_5gram.txt'
             }

    def __init__(self, kind=None):
        self._kind = kind if kind in self.KINDS.keys() else 0
        self._min_ngram = 2
        self._delimiter = ';'
        self._ngram = self.KINDS[self._kind]
        self._tagger = Mecab()
        self._vocab = self.get_vocab()
        self._stopwords = self.get_wordset(self.FILES['stopwords'])
        self._stopngrams = self.get_wordset(self.FILES['stopngrams'])
        self._startwords = self.get_wordset(self.FILES['startwords']) if self._kind == 0 else None
        self._keepwords = self.extract_words(self._vocab) if self._kind == 1 else None

    def tokenize(self, text):
        if type(text) == list:
            ngram_tokens = []
            for t in text:
                tokens = self._tagger.sent_words(t)
                ngram_tokens += self.ngramize(tokens)
        else:
            tokens = self._tagger.sent_words(text)
            ngram_tokens = self.ngramize(tokens)
        return ngram_tokens

    def ngramize(self, tokens):
        ngram_tokens = []
        if self._keepwords:
            tokens = [w for w in tokens if w in self._keepwords]
        else:
            tokens = [w for w in tokens if w not in self._stopwords]
        for pos in range(len(tokens)):
            for gram in range(self._min_ngram, self._ngram + 1):
                token = self.get_ngram(tokens, pos, gram, self._startwords)
                if token:
                    if token in self._vocab:
                        ngram_tokens.append(token)
        filtered_tokens = []
        if len(ngram_tokens) > 0:
            ngram_tokens = sorted(ngram_tokens, key=lambda item: len(item.split(';')), reverse=True)
            for token in ngram_tokens:
                existing_token = False
                for check_token in filtered_tokens:
                    if token in check_token:
                        existing_token = True
                        break
                if not existing_token:
                    filtered_tokens.append(token)

        return filtered_tokens

    def get_ngram(self, tokens, pos, gram, startwords=None):
        if pos < 0:
            return None
        if pos + gram > len(tokens):
            return None
        token = tokens[pos]
        check_verb = False
        if startwords:
            if token in startwords:
                for i in range(1, gram):
                    if tokens[pos + i] not in token:
                        if 'VV' in tokens[pos + i] or 'VVX' in tokens[pos + i]:
                            check_verb = True
                        token += self._delimiter + tokens[pos + i]
                if len(token.split(self._delimiter)) == gram and check_verb:
                    return token
                else:
                    return None
            elif 'VA' in token or 'VAX' in token:
                if tokens[pos + 1] in startwords:
                    token = token + self._delimiter + tokens[pos + 1]
                    for i in range(2, gram):
                        if tokens[pos + i] not in token:
                            if 'VV' in tokens[pos + i] or 'VVX' in tokens[pos + i]:
                                check_verb = True
                            token += self._delimiter + tokens[pos + i]
                    if len(token.split(self._delimiter)) == gram and check_verb:
                        return token
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            if 'VA' in token or 'VAX' in token or 'NNG' in token:
                for i in range(1, gram):
                    if tokens[pos + i] not in token:
                        token += self._delimiter + tokens[pos + i]
                if len(token.split(self._delimiter)) == gram and 'NNG' in token and 'VV' in token:
                    return token
                else:
                    return None
            else:
                return None

    def get_wordset(self, files):
        wordset = set()
        for f in files:
            fin = open('%s/%s' % (LEXICON_PATH, f), 'r', encoding='utf-8')
            for line in fin.readlines():
                word = line.strip().split()[0]
                if len(word) > 1:
                    wordset.add(word)
            fin.close()
        return wordset

    def get_vocab(self):
        vocab = {}
        vocab_path = os.path.join(LEXICON_PATH, self.FILES['vocab'])
        with open(vocab_path) as f:
            for i, line in enumerate(f):
                w = line.strip().split()
                if len(w[0]) > 0:
                    vocab[w[0]] = w[1]
        return vocab

    def extract_words(self, vocab):
        words = []
        for line in vocab.keys() if type(vocab) == dict else vocab:
            tokens = line.split(self._delimiter)
            for pos in range(len(tokens)):
                token = tokens[pos]
                if token not in words:
                    words.append(token)
        return words


class Tokenizer(BaseTokenizer):
    '''
    The default tokenizer, which only takes care of words made up of ``[a-z]+``.
    The output of the tokenizer is stemmed by ``nltk.PorterStemmer``. 
    
    The stoplist from https://www3.nd.edu/~mcdonald/Word_Lists.html is included in this
    tokenizer. Any word in the stoplist will be excluded from the output.
    '''

    def __init__(self):
        self._stemmer = nltk.PorterStemmer()
        self._stopset = self.get_stopset()

    def tokenize(self, text):
        tokens = []
        for t in nltk.regexp_tokenize(text.lower(), '[a-z]+'):
            t = self._stemmer.stem(t)
            if t not in self._stopset:
                tokens.append(t)
        return tokens

    # def ngramize(self, tokens):
    #     return tokens

    def get_stopset(self):
        files = ['Currencies.txt', 'DatesandNumbers.txt', 'Generic.txt', 'Geographic.txt',
                 'Names.txt']
        stopset = set()
        for f in files:
            fin = open('%s/%s' % (LEXICON_PATH, f), 'rb')
            for line in fin.readlines():
                line = line.decode(encoding='latin-1')
                match = re.search('(\w+)', line)
                if match is None:
                    continue
                word = match.group(1)
                stopset.add(self._stemmer.stem(word.lower()))
            fin.close()
        return stopset
