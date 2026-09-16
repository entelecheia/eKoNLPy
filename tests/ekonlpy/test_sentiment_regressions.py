import pytest

from ekonlpy.sentiment import HIV4, LM
from ekonlpy.sentiment.utils import calc_polarity


class FixedTokenizer:
    def tokenize(self, text):
        return ["custom", text]


@pytest.mark.parametrize("sentiment_class", [LM, HIV4])
def test_lm_and_hiv4_construct_and_score(sentiment_class):
    sentiment = sentiment_class()

    # These ordinary words exercise the public tokenize -> get_score path;
    # their stems are present in both shipped dictionaries.
    positive_score = sentiment.get_score(sentiment.tokenize("abundance"))
    negative_score = sentiment.get_score(sentiment.tokenize("abandon"))

    assert positive_score["Positive"] == 1
    assert negative_score["Negative"] == -1
    assert sentiment.get_score([]) == {
        "Positive": 0,
        "Negative": 0,
        "Polarity": 0.0,
        "Subjectivity": 0.0,
    }


@pytest.mark.parametrize("sentiment_class", [LM, HIV4])
def test_dictionary_loading_does_not_replace_custom_tokenizer(sentiment_class):
    tokenizer = FixedTokenizer()
    sentiment = sentiment_class(tokenizer=tokenizer)

    assert sentiment._tokenizer is tokenizer
    assert sentiment.tokenize("phrase") == ["custom", "phrase"]


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ([-1, -1], pytest.approx(-1)),
        ([2, -1], pytest.approx(1 / 2)),
        ([2, -1, -1], pytest.approx(0)),
        ([2, -1, -1, -1], pytest.approx(-0.25)),
        ([], 0),
        ([0, 0], 0),
    ],
)
def test_calc_polarity_weighted_uses_both_signs_in_denominator(scores, expected):
    assert calc_polarity(scores, by_count=False) == expected


def test_calc_polarity_preserves_empty_and_counted_behavior():
    assert calc_polarity([]) == 0.0
    assert calc_polarity([2, -1]) == pytest.approx(0.0)


def _tiny_classifier():
    from nltk.classify import NaiveBayesClassifier

    train = [
        ({"good": True, "nice": True, "great": True}, "pos"),
        ({"good": True, "nice": True}, "pos"),
        ({"good": True}, "pos"),
        ({"bad": True, "awful": True, "terrible": True}, "neg"),
        ({"bad": True, "awful": True}, "neg"),
        ({"bad": True}, "neg"),
    ]
    return NaiveBayesClassifier.train(train)


def test_mpck_informative_features_normalize_negative_polarities():
    from ekonlpy.sentiment.mpck import MPCK

    mpck = MPCK(classifier=_tiny_classifier())
    features = mpck.get_informative_features()

    labels = {f.Label for f in features}
    assert labels == {1, -1}
    for f in features:
        assert -1 <= f.Polarity <= 1


def test_get_vocab_skips_blank_lines_and_rejects_single_field_rows(tmp_path):
    from ekonlpy.sentiment.mpck import MPCK
    from ekonlpy.sentiment.utils import MPTokenizer

    good = tmp_path / "good.txt"
    good.write_text("hawkish pos\n\ndovish neg\n", encoding="utf-8")
    bad = tmp_path / "bad.txt"
    bad.write_text("hawkish pos\norphan\n", encoding="utf-8")

    mpck = MPCK.__new__(MPCK)
    tokenizer = MPTokenizer.__new__(MPTokenizer)

    for reader in (mpck, tokenizer):
        assert reader.get_vocab(str(good)) == {"hawkish": "pos", "dovish": "neg"}
        with pytest.raises(ValueError, match=r"bad\.txt:2"):
            reader.get_vocab(str(bad))


def test_get_wordset_skips_blank_lines(tmp_path):
    from ekonlpy.sentiment.utils import MPTokenizer

    path = tmp_path / "wordset.txt"
    path.write_text("금리\n\n인상\n", encoding="utf-8")
    tokenizer = MPTokenizer.__new__(MPTokenizer)

    assert tokenizer.get_wordset([str(path)]) == {"금리", "인상"}


def test_evaluate_confusion_matrix_precision_recall_not_swapped():
    from ekonlpy.sentiment.mpck import evaluate_confusion_matrix

    actual = [1, 1, 1, 1, -1, -1]
    predicted = [1, 1, -1, -1, -1, 1]
    # t_pos=2, f_pos=1, t_neg=1, f_neg=2
    metrics = evaluate_confusion_matrix(actual, predicted)

    assert metrics["Accuracy"] == pytest.approx(0.5)
    assert metrics["Pos precision"] == pytest.approx(2 / 3)
    assert metrics["Pos recall"] == pytest.approx(0.5)
    assert metrics["Neg precision"] == pytest.approx(1 / 3)
    assert metrics["Neg recall"] == pytest.approx(0.5)


def test_evaluate_confusion_matrix_handles_zero_division():
    import warnings

    from ekonlpy.sentiment.mpck import evaluate_confusion_matrix

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        metrics = evaluate_confusion_matrix([1, 1], [-1, -1])

    assert metrics["Accuracy"] == 0.0
    assert metrics["Pos precision"] == 0.0
    assert metrics["Pos recall"] == 0.0
    assert metrics["Neg precision"] == 0.0
    assert metrics["Neg recall"] == 0.0


def test_base_classes_are_abstract():
    from ekonlpy.sentiment.base import BaseDict
    from ekonlpy.sentiment.utils import BaseTokenizer

    with pytest.raises(TypeError):
        BaseTokenizer()
    with pytest.raises(TypeError):
        BaseDict()
