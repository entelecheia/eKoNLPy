import pytest

from ekonlpy.sentiment.utils import KTokenizer, MPTokenizer, calc_polarity


def _ktokenizer(vocab=None):
    tok = KTokenizer.__new__(KTokenizer)
    tok._vocab = vocab
    tok._min_ngram = 1
    tok._ngram = 3
    tok._delimiter = ";"
    tok._skiptags = ["SF", "SP", "SS", "SE", "SO", "SW", "UN", "UV", "UE"]
    return tok


def _mptokenizer():
    tok = MPTokenizer.__new__(MPTokenizer)
    tok._delimiter = ";"
    tok._start_tags = {"NNG", "VA", "VAX", "MAG"}
    tok._noun_tags = {"NNG"}
    return tok


def test_ktokenizer_align_morpheme():
    tok = _ktokenizer()

    assert tok.align_morpheme([("금리", "NNG"), ("인상", "NNG")]) == [
        "금리/NNG",
        "인상/NNG",
    ]


def test_ktokenizer_get_ngram_bounds():
    tok = _ktokenizer()
    tokens = ["금리/NNG", "인상/NNG", "발표/NNG"]

    assert tok.get_ngram(tokens, -1, 1) is None
    assert tok.get_ngram(tokens, 1, 3) is None
    assert tok.get_ngram(tokens, 0, 1) == "금리/NNG"
    assert tok.get_ngram(tokens, 0, 2) == "금리/NNG;인상/NNG"


def test_ktokenizer_ngramize_drops_skiptags_and_filters_vocab():
    tokens = ["금리/NNG", "./SF", "인상/NNG"]

    assert _ktokenizer().ngramize(tokens) == [
        "금리/NNG",
        "금리/NNG;인상/NNG",
        "인상/NNG",
    ]
    assert _ktokenizer(vocab={"금리/NNG": 1}).ngramize(tokens) == ["금리/NNG"]
    assert _ktokenizer(vocab={}).ngramize(tokens) == []


def test_mptokenizer_tokenize_accepts_list_of_sentences():
    tokenizer = MPTokenizer()

    tokens = tokenizer.tokenize(["금리를 인상했다", "물가가 안정됐다"])

    assert isinstance(tokens, list)


def test_mptokenizer_get_ngram_rejects_invalid_start():
    tok = _mptokenizer()

    assert tok.get_ngram(["금리/NNG"], -1, 1) is None
    assert tok.get_ngram(["했다/EF"], 0, 1) is None
    assert tok.get_ngram(["금리"], 0, 1) is None


def test_mptokenizer_get_ngram_skips_repeated_adjacent_tokens():
    tok = _mptokenizer()

    assert tok.get_ngram(["금리/NNG", "금리/NNG"], 0, 2) == "금리/NNG"
    assert tok.get_ngram(["금리/NNG", "인상/NNG"], 0, 2) == "금리/NNG;인상/NNG"


def test_calc_polarity_by_count_and_by_score():
    assert calc_polarity([1, 1, -1]) == pytest.approx(1 / 3, abs=1e-3)
    assert calc_polarity([0.9, -0.1], by_count=False) == pytest.approx(0.4, abs=1e-3)
