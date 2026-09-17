import pytest

from ekonlpy.sentiment import EUKO


def test_euko_construct_and_score_from_dictionary_terms():
    euko = EUKO()

    pos_term = next(iter(euko._posdict))
    neg_term = next(iter(euko._negdict))

    score = euko.get_score([pos_term])
    assert score["Positive"] == 1
    assert score["Negative"] == 0

    score = euko.get_score([neg_term])
    assert score["Negative"] == -1

    score = euko.get_score([pos_term, neg_term])
    assert score["Polarity"] == pytest.approx(0.0)
    assert score["Subjectivity"] == pytest.approx(1.0)


def test_euko_get_score_by_count_false_uses_polarity_values():
    euko = EUKO()

    pos_term = next(iter(euko._posdict))
    score = euko.get_score([pos_term], by_count=False)

    assert score["Positive"] == pytest.approx(euko._poldict[pos_term])


def test_euko_tokenize_korean_text_returns_list():
    euko = EUKO()

    tokens = euko.tokenize("한국은행이 금리를 인상했다")

    assert isinstance(tokens, list)


def test_euko_kind_one_uses_lex_lexicon():
    euko = EUKO(kind=1)

    assert euko._posdict and euko._negdict
    assert euko._intensity_cutoff == pytest.approx(1.3)


def test_euko_invalid_kind_falls_back_to_default():
    euko = EUKO(kind=99)

    assert euko._intensity_cutoff == pytest.approx(2.0)


def test_euko_custom_intensity_cutoff_is_capped():
    euko = EUKO(intensity_cutoff=5.0)

    assert euko._intensity_cutoff == 3
    assert euko._posdict and euko._negdict
