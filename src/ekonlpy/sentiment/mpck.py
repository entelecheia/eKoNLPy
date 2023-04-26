"""
This module contains classes for monetary policy sentiment classifier.
"""

import os
import pickle
from collections import defaultdict, namedtuple

import nltk
import numpy as np
from nltk.classify import NaiveBayesClassifier
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.metrics.scores import precision, recall
from nltk.probability import ConditionalFreqDist, FreqDist
from scipy.stats import pearsonr, spearmanr

from ..data.tagset import aux_tags
from ..tag import Mecab
from ..utils.io import installpath
from .base import LEXICON_PATH

MODEL_PATH = "%s/data/model" % installpath


class MPCK(object):
    """
    A class for monetary policy sentiment classifier.
    """

    FILES = {"vocab": "mpko/mp_polarity_vocab.txt"}

    def __init__(self, classifier: NaiveBayesClassifier = None):
        if classifier is None:
            self.load_default_classifier()
        else:
            self.classifier = classifier
        self._tokenizer = Mecab()
        self._vocab = self.get_vocab(self.FILES["vocab"])
        self._positive_label = "pos"
        self._negative_label = "neg"
        self._min_ngram = 2
        self._ngram = 5
        self._delimiter = ";"
        self._start_tags = {"NNG", "VA", "VAX", "MAG"}
        self._noun_tags = {"NNG"}
        self._aux_tags = aux_tags
        self._auxwords = {"못하/VX", "아니/VCN", "않/VX", "지만/VCP"}

    def get_vocab(self, file):
        vocab = {}
        vocab_path = os.path.join(LEXICON_PATH, file)
        with open(vocab_path) as f:
            for i, line in enumerate(f):
                w = line.strip().split()
                if len(w[0]) > 0:
                    vocab[w[0]] = w[1]
        return vocab

    def load_default_classifier(self):
        classifier_path = os.path.join(MODEL_PATH, "MPKC.nbc")
        self.load_classifier(classifier_path)

    def load_classifier(self, file_path):
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                self.classifier = pickle.load(f)
        else:
            raise ValueError("There is no classifier file.")

    def save_classifier(self, file_path):
        with open(file_path, "wb") as f:
            pickle.dump(self.classifier, f)
        print("Save the classifier to the file: {}".format(file_path))

    def tokenize(self, text):
        tokens = self._tokenizer.sent_words(text)
        tokens = [
            w
            for w in tokens
            if (
                (w.split("/")[1] if "/" in w else None) not in self._aux_tags
                or w in self._auxwords
            )
        ]
        return tokens

    def ngramize(self, tokens, keep_overlapping_ngram=False):
        ngram_tokens = []

        for pos in range(len(tokens)):
            for gram in range(self._min_ngram, self._ngram + 1):
                token = self.get_ngram(tokens, pos, gram)
                if token:
                    if token in self._vocab:
                        ngram_tokens.append(token)
        if not keep_overlapping_ngram:
            filtered_tokens = []
            if len(ngram_tokens) > 0:
                ngram_tokens = sorted(
                    ngram_tokens, key=lambda item: len(item), reverse=True
                )
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

    def get_ngram(self, tokens, pos, gram):
        if pos < 0:
            return None
        if pos + gram > len(tokens):
            return None
        token = tokens[pos]
        check_noun = False

        tag = token.split("/")[1] if "/" in token else None
        if tag in self._start_tags:
            if tag in self._noun_tags:
                check_noun = True
            for i in range(1, gram):
                if tokens[pos + i] != tokens[pos + i - 1]:
                    tag = (
                        tokens[pos + i].split("/")[1]
                        if "/" in tokens[pos + i]
                        else None
                    )
                    if tag in self._noun_tags:
                        check_noun = True
                    token += self._delimiter + tokens[pos + i]
            if check_noun:
                return token
            else:
                return None
        else:
            return None

    def classify(self, tokens, intensity_cutoff=1.3):
        eps = 1e-6
        features = {token: True for token in tokens}
        result = self.classifier.prob_classify(features)
        pos_score = result.prob(self._positive_label)
        neg_score = result.prob(self._negative_label)
        polarity = pos_score - neg_score
        intensity = (
            pos_score / (neg_score + eps)
            if polarity > 0
            else neg_score / (pos_score + eps)
        )
        polarity = polarity if intensity > intensity_cutoff else 0
        return {
            "Polarity": polarity,
            "Intensity": intensity,
            "Pos score": pos_score,
            "Neg score": neg_score,
        }

    def get_informative_features(self, cutoff_ratio=1.2):
        cpdist = (
            self.classifier._feature_probdist
        )  # probability distribution for feature values given labels
        fcnt = len(set([w for _, w in cpdist.keys()]))
        feature_list = []
        epsilon = 1e-6
        feature = namedtuple("Feature", ["Word", "Label", "Polarity", "Intensity"])

        for feature_name, feature_val in self.classifier.most_informative_features(
            n=fcnt
        ):

            def labelprob(label):
                return cpdist[label, feature_name].prob(feature_val)

            labels = sorted(
                [
                    label
                    for label in self.classifier._labels
                    if feature_val in cpdist[label, feature_name].samples()
                ],
                key=labelprob,
            )
            l0 = labels[0]
            l1 = labels[-1]
            l0_p = cpdist[l0, feature_name].prob(feature_val) + epsilon
            l1_p = cpdist[l1, feature_name].prob(feature_val) + epsilon
            ratio = l1_p / l0_p
            if ratio > cutoff_ratio:
                polar = ratio if l1 == self._positive_label else 1 / ratio
                label = 1 if l1 == self._positive_label else -1
                feature_list.append(feature(feature_name, label, polar, ratio))

        p = [f.Polarity for f in feature_list if f.Label > 0]
        n = [f.Polarity for f in feature_list if f.Label > 0]
        for i, f in enumerate(feature_list):
            if f.Label > 0:
                feature_list[i] = f._replace(
                    Polarity=(f.Polarity - np.min(p)) / (np.max(p) - np.min(p))
                )
            elif f.Label < 0:
                feature_list[i] = f._replace(
                    Polarity=(f.Polarity - np.max(n)) / (np.max(n) - np.min(n))
                )

        return feature_list

    def bagging_classifier(
        self,
        dataset,
        iterations=20,
        feature_fn_name="word",
        train_ratio=0.8,
        best_words_ratio=0.8,
        verbose=False,
        token_column="text",
        target_column="category",
        pos_target_val=1,
        neg_target_val=-1,
    ):
        """
        Bootstrap aggregating classifiers
        """

        if verbose:
            print(
                "\nNo. of iterations: {}. feature function: {}, train ratio: {}, best words ratio: {}".format(
                    iterations, feature_fn_name, train_ratio, best_words_ratio
                )
            )

        clfs = []
        mlst = []

        for i in range(iterations):
            classifier, metrics = self.train_classifier(
                dataset,
                feature_fn_name=feature_fn_name,
                verbose=False,
                train_ratio=train_ratio,
                best_ratio=best_words_ratio,
                token_column=token_column,
                target_column=target_column,
                pos_target_val=pos_target_val,
                neg_target_val=neg_target_val,
            )
            clfs.append(classifier)
            mlst.append(metrics)

        mean_metrics = {}
        best_index = 0
        best_accuracy = 0
        for i, metrics in enumerate(mlst):
            if metrics["Accuracy"] > best_accuracy:
                best_accuracy = metrics["Accuracy"]
                best_index = i
            if i == 0:
                for key in metrics.keys():
                    mean_metrics[key] = metrics[key]
            else:
                for key in mean_metrics.keys():
                    mean_metrics[key] += metrics[key]
        for key in mean_metrics.keys():
            mean_metrics[key] = mean_metrics[key] / len(mlst)
        if verbose:
            print("Best classifier: {}".format(best_index))
            print(mlst[best_index])
            print("- Average metrics of classifiers -")
            print(mean_metrics)

        return best_index, clfs, mlst, mean_metrics

    def train_classifier(
        self,
        dataset,
        feature_fn_name="word",
        train_ratio=0.8,
        verbose=False,
        token_column="text",
        target_column="category",
        best_ratio=0.8,
        pos_target_val=1,
        neg_target_val=-1,
    ):
        def word_feats(words):
            return dict([(word, True) for word in words])

        def best_word_feats(words):
            return dict([(word, True) for word in words if word in bestwords])

        def best_bigram_word_feats(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
            bigram_finder = BigramCollocationFinder.from_words(words)
            bigrams = bigram_finder.nbest(score_fn, n)
            d = dict([(bigram, True) for bigram in bigrams])
            d.update(best_word_feats(words))
            return d

        def best_trigram_word_feats(words, score_fn=TrigramAssocMeasures.chi_sq, n=200):
            tcf = TrigramCollocationFinder.from_words(words)
            trigrams = tcf.nbest(score_fn, n)
            d = dict([(trigram, True) for trigram in trigrams])
            d.update(best_bigram_word_feats(words))
            d.update(best_word_feats(words))
            return d

        if verbose:
            print(
                "\nSelected feature function: {}, token column: {}, train ratio: {}".format(
                    feature_fn_name, token_column, train_ratio
                )
            )
        df = dataset.sample(frac=1).reset_index(drop=True)
        negids = df[df[target_column] == neg_target_val].index
        posids = df[df[target_column] == pos_target_val].index
        feats = df[token_column]

        if feature_fn_name in ["best_word", "best_bigram", "best_trigram"]:
            word_fd = FreqDist()
            label_word_fd = ConditionalFreqDist()
            for tokens in df[df[target_column] == pos_target_val][token_column]:
                for word in tokens.split():
                    word_fd[word] += 1
                    label_word_fd[self._positive_label][word] += 1

            for tokens in df[df[target_column] == neg_target_val][token_column]:
                for word in tokens.split():
                    word_fd[word] += 1
                    label_word_fd[self._negative_label][word] += 1

            pos_word_count = label_word_fd[self._positive_label].N()
            neg_word_count = label_word_fd[self._negative_label].N()
            total_word_count = pos_word_count + neg_word_count
            word_scores = {}
            for word, freq in word_fd.items():
                pos_score = BigramAssocMeasures.chi_sq(
                    label_word_fd[self._positive_label][word],
                    (freq, pos_word_count),
                    total_word_count,
                )
                neg_score = BigramAssocMeasures.chi_sq(
                    label_word_fd[self._negative_label][word],
                    (freq, neg_word_count),
                    total_word_count,
                )
                word_scores[word] = pos_score + neg_score

            best_cnt = int(len(word_scores) * best_ratio)
            best = sorted(word_scores.items(), key=lambda item: item[1], reverse=True)[
                :best_cnt
            ]
            bestwords = set([w for w, s in best])
            if feature_fn_name == "best_trigram_word_feats":
                feat_fn = best_trigram_word_feats
            elif feature_fn_name == "best_bigram":
                feat_fn = best_bigram_word_feats
            else:
                feat_fn = best_word_feats

        else:
            feat_fn = word_feats

        negfeats = [(feat_fn(feats[i].split()), self._negative_label) for i in negids]
        posfeats = [(feat_fn(feats[i].split()), self._positive_label) for i in posids]
        if verbose:
            print(
                "No. of samples: {}, Pos: {}, Neg: {}".format(
                    len(feats), len(posfeats), len(negfeats)
                )
            )

        negcutoff = int(len(negfeats) * train_ratio)
        poscutoff = int(len(posfeats) * train_ratio)

        trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
        testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]

        classifier = NaiveBayesClassifier.train(trainfeats)
        refsets = defaultdict(set)
        testsets = defaultdict(set)

        for i, (feats, label) in enumerate(testfeats):
            refsets[label].add(i)
            observed = classifier.classify(feats)
            testsets[observed].add(i)

        metrics = {
            "Accuracy": nltk.classify.util.accuracy(classifier, testfeats),
            "Pos precision": precision(
                refsets[self._positive_label], testsets[self._positive_label]
            ),
            "Pos recall": recall(
                refsets[self._positive_label], testsets[self._positive_label]
            ),
            "Neg precision": precision(
                refsets[self._negative_label], testsets[self._negative_label]
            ),
            "Neg recall": recall(
                refsets[self._negative_label], testsets[self._negative_label]
            ),
        }
        if verbose:
            print(metrics)

        return classifier, metrics

    def evaluate_confusion_matrix(
        self, actual, predicted, actual_pos_val=1, actual_neg_val=-1, verbose=False
    ):
        return evaluate_confusion_matrix(
            actual,
            predicted,
            actual_pos_val=actual_pos_val,
            actual_neg_val=actual_neg_val,
            verbose=verbose,
        )


def evaluate_confusion_matrix(
    actual, predicted, actual_pos_val=1, actual_neg_val=-1, verbose=False
):
    t_pos = 0
    f_pos = 0
    t_neg = 0
    f_neg = 0
    for a, p in zip(actual, predicted):
        if p > 0:
            if a == actual_pos_val:
                t_pos += 1
            elif a == actual_neg_val:
                f_neg += 1
        elif p < 0:
            if a == actual_neg_val:
                t_neg += 1
            elif a == actual_pos_val:
                f_pos += 1

    pr = pearsonr(actual, predicted)
    sr = spearmanr(actual, predicted)
    all_acc = (t_pos + t_neg) / (t_pos + f_pos + t_neg + f_neg)
    pos_acc, pos_recall = t_pos / (t_pos + f_pos), t_pos / (t_pos + f_neg)
    neg_acc, neg_recall = t_neg / (t_neg + f_neg), t_neg / (t_neg + f_pos)
    metrics = {
        "Pearson corr": pr[0],
        "Spearman corr": sr[0],
        "Accuracy": all_acc,
        "Pos precision": pos_acc,
        "Pos recall": pos_recall,
        "Neg precision": neg_acc,
        "Neg recall": neg_recall,
    }
    if verbose:
        print(metrics)
    return metrics
