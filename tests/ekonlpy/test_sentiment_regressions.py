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
