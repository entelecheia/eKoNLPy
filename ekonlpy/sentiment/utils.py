'''
This module contains methods to tokenize sentences.
'''
import abc
import re
import nltk
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

    @abc.abstractmethod
    def ngramize(self, tokens):
        '''Return n-gramized temrs.

        :type tokens: list of tokens

        :returns: list
        '''
        pass


class MPTokenizer(BaseTokenizer):
    '''
    The default tokenizer for MPKO sub class, which yields 5-gram tokens.
    The output of the tokenizer is tagged by Mecab.
    '''

    def __init__(self):
        self._tagger = Mecab()
        self._stopset = self.get_stopset()
        self._vocab = self.get_vocab()

    def tokenize(self, text):
        tagged = self._tagger.pos(text)
        tokens = ['{}/{}'.format(w.lower(), t.split('+')[0]) for w, t in tagged
                  if t in self._tagger.sent_tags and w.lower() not in self._tagger.stopwords]
        return tokens

    def ngramize(self, tokens):
        ngram = 5
        min_ngram = 3
        ngram_tokens = []
        tokens = [w for w in tokens if w not in self._stopset]
        for pos in range(len(tokens)):
            for gram in range(min_ngram, ngram + 1):
                token = self.get_ngram(tokens, pos, gram)
                if token is None:
                    continue
                if token in self._vocab:
                    ngram_tokens.append(token)
        return ngram_tokens

    def get_ngram(self, tokens, pos, gram, delimiter='@$'):  # uni:gram=1  bi:gram=2 tri:gram=3
        if pos < 0:
            return None
        if pos + gram > len(tokens):
            return None
        token = tokens[pos]
        if 'NNG' in token:
            for i in range(1, gram):
                if tokens[pos + i] not in token:
                    token = token + delimiter + tokens[pos + i]
            if len(token.split(delimiter)) == gram:
                return token
            else:
                return None
        else:
            return None

    def get_stopset(self):
        files = ['MPS_stopwords.txt']
        stopset = set()
        for f in files:
            fin = open('%s/%s' % (LEXICON_PATH, f), 'r', encoding='utf-8')
            for line in fin.readlines():
                word = line.strip()
                if len(word) > 1:
                    stopset.add(word)
            fin.close()
        return stopset

    def get_vocab(self):
        vocab = {}
        vocab_path = os.path.join(LEXICON_PATH, 'MPS_vocab_5gram.txt')
        with open(vocab_path) as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                if len(line) > 0:
                    w = line.split()
                    vocab[w[0]] = w[1]
        return vocab


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

    def ngramize(self, tokens):
        return tokens

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
