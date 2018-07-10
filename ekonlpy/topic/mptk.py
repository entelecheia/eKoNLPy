'''
This module contains classes for topic analysis.
'''

import os
from ekonlpy.tag import Mecab
from ekonlpy.utils import installpath
from gensim.corpora import Dictionary
from gensim.models import LdaModel

MODEL_PATH = '%s/data/model' % installpath


class MPTK(object):
    '''
    A class for monetary policy topic analysis.
    '''

    def __init__(self, num_topics=36):
        self._topic = {}
        self._topic_names = {}
        self._id2word = None
        self._lda = None
        self.num_topics = num_topics
        self._load_topic_names(num_topics)
        self._load_model(num_topics)
        self._tokenizer = Mecab()

    def tokenize(self, text):
        return self._tokenizer.pos(text)

    def nouns(self, phrase):
        return self._tokenizer.nouns(phrase)

    def doc2bow(self, document):
        return self._id2word.doc2bow(document)

    def get_document_topic(self, bow, include_names=False, min_weight=None):
        dtm = self._lda[bow]
        if min_weight:
            dtm = [(i, w) for i, w in dtm if w > min_weight]
        if include_names:
            dtm = [(i, self._topic[i], w) for i, w in dtm]
        return dtm

    def topic_name(self, topic_id):
        if topic_id in self._topic.keys():
            return self._topic[topic_id]

    def _load_model(self, num_topics):
        dict_path = os.path.join(MODEL_PATH, 'mp_corpus.dict')
        lda_path = os.path.join(MODEL_PATH, 'mp_topic_model-k{}.lda'.format(num_topics))
        if os.path.isfile(lda_path):
            self._id2word = Dictionary.load(dict_path)
            self._lda = LdaModel.load(lda_path)

    def _load_topic_names(self, num_topics):
        file_path = os.path.join(MODEL_PATH, 'mp_topic_titles-k{}.txt'.format(num_topics))
        if os.path.isfile(file_path):
            with open(file_path) as f:
                for i, line in enumerate(f):
                    if len(line) > 0:
                        w = line.split(':')
                        self._topic_names[w[0].strip()] = w[1].strip()
                        self._topic[i] = w[1].strip()
