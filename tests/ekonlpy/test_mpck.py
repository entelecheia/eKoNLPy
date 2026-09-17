import pandas as pd
import pytest
from nltk.classify import NaiveBayesClassifier

from ekonlpy.sentiment.mpck import MPCK
from ekonlpy.sentiment.utils import MPTokenizer


def _tiny_classifier():
    train = [
        ({"good": True, "nice": True, "great": True}, "pos"),
        ({"good": True, "nice": True}, "pos"),
        ({"good": True}, "pos"),
        ({"bad": True, "awful": True, "terrible": True}, "neg"),
        ({"bad": True, "awful": True}, "neg"),
        ({"bad": True}, "neg"),
    ]
    return NaiveBayesClassifier.train(train)


def _tiny_dataset():
    return pd.DataFrame(
        {
            "text": [
                "good nice great",
                "good nice",
                "good great",
                "bad awful terrible",
                "bad awful",
                "bad terrible",
            ],
            "category": [1, 1, 1, -1, -1, -1],
        }
    )


@pytest.fixture()
def mpck():
    return MPCK(classifier=_tiny_classifier())


def test_mpck_default_classifier_scores_korean_text():
    mpck = MPCK()

    scores = mpck.classify(mpck.tokenize("한국은행이 기준금리를 인상했다"))

    assert set(scores) == {"Polarity", "Intensity", "Pos score", "Neg score"}


def test_tokenize_korean_text(mpck):
    tokens = mpck.tokenize("한국은행이 금리를 인상했다")

    assert isinstance(tokens, list)


def test_classify_returns_probabilities(mpck):
    result = mpck.classify(["good"])

    assert result["Pos score"] > result["Neg score"]
    assert result["Polarity"] > 0

    result = mpck.classify(["bad"])

    assert result["Neg score"] > result["Pos score"]


def test_get_ngram_out_of_range_and_tag_filters(mpck):
    tokens = ["금리/NNG", "인상/NNG"]

    assert mpck.get_ngram(tokens, -1, 2) is None
    assert mpck.get_ngram(tokens, 0, 3) is None
    assert mpck.get_ngram(["했다/VV"], 0, 1) is None
    assert mpck.get_ngram(["좋/VA", "다/EF"], 0, 2) is None
    assert mpck.get_ngram(tokens, 0, 2) == "금리/NNG;인상/NNG"


def test_get_ngram_skips_duplicate_adjacent_tokens(mpck):
    tokens = ["금리/NNG", "금리/NNG"]

    assert mpck.get_ngram(tokens, 0, 2) == "금리/NNG"


def test_ngramize_collects_vocab_ngrams(mpck):
    mpck._vocab = {"금리/NNG;인상/NNG": "pos"}
    tokens = ["금리/NNG", "인상/NNG"]

    assert mpck.ngramize(tokens) == ["금리/NNG;인상/NNG"]
    assert mpck.ngramize(tokens, keep_overlapping_ngram=True) == ["금리/NNG;인상/NNG"]


def test_ngramize_drops_overlapping_shorter_ngrams(mpck):
    mpck._vocab = {
        "금리/NNG;인상/NNG;상승/NNG": "pos",
        "인상/NNG;상승/NNG": "pos",
    }
    tokens = ["금리/NNG", "인상/NNG", "상승/NNG"]

    assert mpck.ngramize(tokens) == ["금리/NNG;인상/NNG;상승/NNG"]
    assert mpck.ngramize(tokens, keep_overlapping_ngram=True) == [
        "금리/NNG;인상/NNG;상승/NNG",
        "인상/NNG;상승/NNG",
    ]


def test_ngramize_without_vocab_hits_returns_empty(mpck):
    mpck._vocab = {}

    assert mpck.ngramize(["금리/NNG", "인상/NNG"]) == []


def test_train_classifier_with_word_features(mpck):
    classifier, metrics = mpck.train_classifier(
        _tiny_dataset(), feature_fn_name="word", train_ratio=0.7
    )

    assert isinstance(classifier, NaiveBayesClassifier)
    assert 0.0 <= metrics["Accuracy"] <= 1.0


def test_train_classifier_with_best_word_features(mpck):
    classifier, metrics = mpck.train_classifier(
        _tiny_dataset(), feature_fn_name="best_word", train_ratio=0.7
    )

    assert isinstance(classifier, NaiveBayesClassifier)
    assert 0.0 <= metrics["Accuracy"] <= 1.0


def test_bagging_classifier_returns_best_and_mean_metrics(mpck):
    best_index, clfs, mlst, mean_metrics = mpck.bagging_classifier(
        _tiny_dataset(), iterations=2, feature_fn_name="word", train_ratio=0.7
    )

    assert best_index in (0, 1)
    assert len(clfs) == 2
    assert len(mlst) == 2
    assert 0.0 <= mean_metrics["Accuracy"] <= 1.0


def test_save_and_load_classifier_round_trip(mpck, tmp_path):
    path = tmp_path / "clf.nbc"

    mpck.save_classifier(str(path))
    other = MPCK(classifier=_tiny_classifier())
    other.load_classifier(str(path))

    assert other.classify(["good"]) == mpck.classify(["good"])


def test_load_classifier_rejects_missing_file(mpck, tmp_path):
    with pytest.raises(ValueError, match="no classifier"):
        mpck.load_classifier(str(tmp_path / "missing.nbc"))


def test_evaluate_confusion_matrix_method(mpck):
    metrics = mpck.evaluate_confusion_matrix([1, -1], [1, -1])

    assert metrics["Accuracy"] == pytest.approx(1.0)


def test_get_informative_features_degenerate_groups_no_nan():
    import numpy as np

    train = [
        ({"good": True}, "pos"),
        ({"good": True}, "pos"),
        ({"good": True}, "pos"),
        ({"good": True}, "neg"),
        ({"bad": True}, "neg"),
        ({"bad": True}, "neg"),
        ({"bad": True}, "neg"),
        ({"bad": True}, "pos"),
    ]
    mpck = MPCK(classifier=NaiveBayesClassifier.train(train))

    features = mpck.get_informative_features(cutoff_ratio=1.0)

    assert features
    assert all(np.isfinite(f.Polarity) for f in features)
    assert all(f.Polarity >= 0 for f in features if f.Label > 0)
    assert all(f.Polarity <= 0 for f in features if f.Label < 0)


def test_mptokenizer_get_phrase_joins_surfaces():
    tokenizer = MPTokenizer.__new__(MPTokenizer)
    tokenizer._delimiter = ";"

    assert tokenizer.get_phrase("금리/NNG;인상/NNG") == "금리인상"
