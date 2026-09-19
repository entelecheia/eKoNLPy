"""
This module contains classes for monetary policy sentiment classifier.
"""

import logging
import os
import pickle
from collections import defaultdict, namedtuple
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, ClassVar, Optional

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
from .utils import drop_overlapping, load_ngram_vocab, phrase_ngram

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)

MODEL_PATH = f"{installpath}/data/model"

Feature = namedtuple("Feature", ["Word", "Label", "Polarity", "Intensity"])


class MPCK:
    """
    A class for monetary policy sentiment classifier.
    """

    FILES: ClassVar[dict[str, str]] = {"vocab": "mpko/mp_polarity_vocab.txt"}

    def __init__(self, classifier: Optional[NaiveBayesClassifier] = None):  # type: ignore[no-any-unimported]
        """Initialize the classifier, tokenizer, and vocabulary.

        :param classifier: A trained NaiveBayesClassifier; the default model is loaded if None
        """
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

    def get_vocab(self, file: str) -> dict[str, str]:
        """Load the n-gram vocabulary from the given lexicon file.

        :param file: A lexicon file path relative to the lexicon directory
        :return: A dictionary mapping n-grams to their values
        :raises ValueError: If a vocabulary entry is malformed
        """
        return load_ngram_vocab(file)

    def load_default_classifier(self) -> None:
        """Load the bundled default Naive Bayes classifier."""
        classifier_path = os.path.join(MODEL_PATH, "MPKC.nbc")
        self.load_classifier(classifier_path)

    def load_classifier(self, file_path: str) -> None:
        """Load a pickled classifier from a file.

        :param file_path: Path to the pickled classifier file
        :raises ValueError: If the file does not exist
        """
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                self.classifier = pickle.load(f)  # noqa: S301
        else:
            raise ValueError("There is no classifier file.")  # noqa: TRY003

    def save_classifier(self, file_path: str) -> None:
        """Pickle the classifier to a file.

        :param file_path: Path of the file to write
        """
        with open(file_path, "wb") as f:
            pickle.dump(self.classifier, f)
        logger.info("Save the classifier to the file: %s", file_path)

    def tokenize(self, text: str) -> list[str]:
        """Tag the text with Mecab and filter out auxiliary tags.

        :param text: The input text to tokenize
        :return: A list of "surface/tag" tokens
        """
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

    def ngramize(
        self, tokens: list[str], keep_overlapping_ngram: bool = False
    ) -> list[str]:
        """Generate in-vocabulary n-grams of the tokens.

        :param tokens: A list of "surface/tag" tokens
        :param keep_overlapping_ngram: Whether to keep n-grams that overlap longer n-grams
        :return: A list of n-gram tokens joined by the delimiter
        """
        ngram_tokens: list[str] = []

        for pos in range(len(tokens)):
            for gram in range(self._min_ngram, self._ngram + 1):
                if (
                    token := self.get_ngram(tokens, pos, gram)
                ) and token in self._vocab:
                    ngram_tokens.append(token)
        if not keep_overlapping_ngram:
            ngram_tokens = drop_overlapping(ngram_tokens)

        return ngram_tokens

    def get_ngram(self, tokens: list[str], pos: int, gram: int) -> Optional[str]:
        """Return the n-gram starting at the given position if it forms a valid phrase.

        The n-gram must start with an allowed tag, contain a noun, and have no repeated
        adjacent tokens.

        :param tokens: A list of "surface/tag" tokens
        :param pos: The starting position of the n-gram
        :param gram: The length of the n-gram
        :return: The n-gram token joined by the delimiter, or None if invalid or out of range
        """
        return phrase_ngram(
            tokens, pos, gram, self._start_tags, self._noun_tags, self._delimiter
        )

    def classify(
        self, tokens: list[str], intensity_cutoff: float = 1.3
    ) -> dict[str, float]:
        """Classify the tokens and compute polarity and intensity scores.

        :param tokens: A list of n-gram tokens to use as features
        :param intensity_cutoff: Minimum intensity for a non-zero polarity
        :return: A dictionary with Polarity, Intensity, Pos score, and Neg score
        """
        eps = 1e-6
        features = dict.fromkeys(tokens, True)
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

    def get_informative_features(self, cutoff_ratio: float = 1.2) -> list[Feature]:
        """Return the classifier's informative features with polarity and intensity.

        :param cutoff_ratio: Minimum likelihood ratio for a feature to be included
        :return: A list of Feature namedtuples (Word, Label, Polarity, Intensity)
        """
        cpdist = (
            self.classifier._feature_probdist
        )  # probability distribution for feature values given labels
        fcnt = len({w for _, w in cpdist})
        feature_list: list[Feature] = []
        epsilon = 1e-6

        for feature_name, feature_val in self.classifier.most_informative_features(
            n=fcnt
        ):

            def labelprob(
                label: str, fname: str = feature_name, fval: object = feature_val
            ) -> float:
                """Return the probability of the feature value given the label."""
                return cpdist[label, fname].prob(fval)

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
                feature_list.append(Feature(feature_name, label, polar, ratio))

        p = [f.Polarity for f in feature_list if f.Label > 0]
        n = [f.Polarity for f in feature_list if f.Label < 0]
        for i, f in enumerate(feature_list):
            if f.Label > 0:
                lo, hi = np.min(p), np.max(p)
                polar = 1.0 if hi == lo else (f.Polarity - lo) / (hi - lo)
                feature_list[i] = f._replace(Polarity=polar)
            elif f.Label < 0:
                lo, hi = np.min(n), np.max(n)
                polar = -1.0 if hi == lo else (f.Polarity - hi) / (hi - lo)
                feature_list[i] = f._replace(Polarity=polar)

        return feature_list

    def bagging_classifier(  # type: ignore[no-any-unimported]
        self,
        dataset: "pd.DataFrame",
        iterations: int = 20,
        feature_fn_name: str = "word",
        train_ratio: float = 0.8,
        best_words_ratio: float = 0.8,
        verbose: bool = False,
        token_column: str = "text",  # noqa: S107
        target_column: str = "category",
        pos_target_val: int = 1,
        neg_target_val: int = -1,
    ) -> tuple[int, list[object], list[dict[str, float]], dict[str, float]]:
        """
        Bootstrap aggregating classifiers
        """

        if verbose:
            logger.info(
                "\nNo. of iterations: %d. feature function: %s, train ratio: %s, best words ratio: %s",
                iterations,
                feature_fn_name,
                train_ratio,
                best_words_ratio,
            )

        clfs: list[object] = []
        mlst: list[dict[str, float]] = []

        for _ in range(iterations):
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

        mean_metrics: dict[str, float] = {}
        best_index = 0
        best_accuracy: float = 0
        for i, metrics in enumerate(mlst):
            if metrics["Accuracy"] > best_accuracy:
                best_accuracy = metrics["Accuracy"]
                best_index = i
            if i == 0:
                for key in metrics:
                    mean_metrics[key] = metrics[key]
            else:
                for key, value in mean_metrics.items():
                    value += metrics[key]
        for key in mean_metrics:
            mean_metrics[key] = mean_metrics[key] / len(mlst)
        if verbose:
            logger.info("Best classifier: %d", best_index)
            logger.info("%s", mlst[best_index])
            logger.info("- Average metrics of classifiers -")
            logger.info("%s", mean_metrics)

        return best_index, clfs, mlst, mean_metrics

    def train_classifier(  # type: ignore[no-any-unimported]  # noqa: C901
        self,
        dataset: "pd.DataFrame",
        feature_fn_name: str = "word",
        train_ratio: float = 0.8,
        verbose: bool = False,
        token_column: str = "text",  # noqa: S107
        target_column: str = "category",
        best_ratio: float = 0.8,
        pos_target_val: int = 1,
        neg_target_val: int = -1,
    ) -> tuple[object, dict[str, float]]:
        """Train a Naive Bayes classifier on the dataset and evaluate it on a held-out split.

        :param dataset: A DataFrame with token and target columns
        :param feature_fn_name: Feature function to use ("word", "best_word", "best_bigram", "best_trigram")
        :param train_ratio: Fraction of the data used for training
        :param verbose: Whether to log training details
        :param token_column: Name of the column holding the tokenized text
        :param target_column: Name of the column holding the labels
        :param best_ratio: Fraction of best-scoring words kept for the "best_*" feature functions
        :param pos_target_val: The label value for positive samples
        :param neg_target_val: The label value for negative samples
        :return: A tuple of the trained classifier and its evaluation metrics
        """

        def word_feats(words: list[str]) -> dict[str, bool]:
            """Return a feature dict with all words present."""
            return dict.fromkeys(words, True)

        def best_word_feats(words: list[str]) -> dict[str, bool]:
            """Return a feature dict with the best-scoring words present."""
            return {word: True for word in words if word in bestwords}

        def best_bigram_word_feats(
            words: list[str],
            score_fn: Callable[
                [int, tuple[int, int], int], float
            ] = BigramAssocMeasures.chi_sq,
            n: int = 200,
        ) -> dict[str, bool]:
            """Return a feature dict with the best bigrams and best words present."""
            bigram_finder = BigramCollocationFinder.from_words(words)
            bigrams = bigram_finder.nbest(score_fn, n)
            d = dict.fromkeys(bigrams, True)
            d.update(best_word_feats(words))
            return d

        def best_trigram_word_feats(
            words: list[str],
            score_fn: Callable[
                [int, tuple[int, int, int], tuple[int, int, int], int], float
            ] = TrigramAssocMeasures.chi_sq,
            n: int = 200,
        ) -> dict[str, bool]:
            """Return a feature dict with the best trigrams, bigrams, and words present."""
            tcf = TrigramCollocationFinder.from_words(words)
            trigrams = tcf.nbest(score_fn, n)
            d = dict.fromkeys(trigrams, True)
            d.update(best_bigram_word_feats(words))
            d.update(best_word_feats(words))
            return d

        if verbose:
            logger.info(
                "\nSelected feature function: %s, token column: %s, train ratio: %s",
                feature_fn_name,
                token_column,
                train_ratio,
            )
        df = dataset.sample(frac=1).reset_index(drop=True)
        negids = df[df[target_column] == neg_target_val].index
        posids = df[df[target_column] == pos_target_val].index
        feats = df[token_column]

        feat_fn: Callable[[list[str]], dict[str, bool]]
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
            word_scores: dict[str, float] = {}
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
            bestwords = {w for w, s in best}
            if feature_fn_name == "best_trigram":
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
            logger.info(
                "No. of samples: %d, Pos: %d, Neg: %d",
                len(feats),
                len(posfeats),
                len(negfeats),
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
            logger.info("%s", metrics)

        return classifier, metrics

    def evaluate_confusion_matrix(
        self,
        actual: Sequence[float],
        predicted: Sequence[float],
        actual_pos_val: int = 1,
        actual_neg_val: int = -1,
        verbose: bool = False,
    ) -> dict[str, float]:
        """Evaluate predictions against actual labels with a confusion matrix.

        :param actual: The actual labels
        :param predicted: The predicted scores
        :param actual_pos_val: The label value for positive samples
        :param actual_neg_val: The label value for negative samples
        :param verbose: Whether to log the metrics
        :return: A dictionary of evaluation metrics
        """
        return evaluate_confusion_matrix(
            actual,
            predicted,
            actual_pos_val=actual_pos_val,
            actual_neg_val=actual_neg_val,
            verbose=verbose,
        )


def evaluate_confusion_matrix(
    actual: Sequence[float],
    predicted: Sequence[float],
    actual_pos_val: int = 1,
    actual_neg_val: int = -1,
    verbose: bool = False,
) -> dict[str, float]:
    """Evaluate predictions against actual labels with a confusion matrix.

    :param actual: The actual labels
    :param predicted: The predicted scores
    :param actual_pos_val: The label value for positive samples
    :param actual_neg_val: The label value for negative samples
    :param verbose: Whether to log the metrics
    :return: A dictionary of evaluation metrics including correlations, accuracy, precision, and recall
    """
    t_pos = 0
    f_pos = 0
    t_neg = 0
    f_neg = 0
    for a, p in zip(actual, predicted):
        if p > 0:
            if a == actual_pos_val:
                t_pos += 1
            elif a == actual_neg_val:
                f_pos += 1
        elif p < 0:
            if a == actual_neg_val:
                t_neg += 1
            elif a == actual_pos_val:
                f_neg += 1

    def ratio(numerator: float, denominator: float) -> float:
        """Return numerator / denominator, or 0.0 if the denominator is zero."""
        return numerator / denominator if denominator else 0.0

    pr = pearsonr(actual, predicted)
    sr = spearmanr(actual, predicted)
    metrics = {
        "Pearson corr": pr[0],
        "Spearman corr": sr[0],
        "Accuracy": ratio(t_pos + t_neg, t_pos + f_pos + t_neg + f_neg),
        "Pos precision": ratio(t_pos, t_pos + f_pos),
        "Pos recall": ratio(t_pos, t_pos + f_neg),
        "Neg precision": ratio(t_neg, t_neg + f_neg),
        "Neg recall": ratio(t_neg, t_neg + f_pos),
    }
    if verbose:
        logger.info("%s", metrics)
    return metrics
