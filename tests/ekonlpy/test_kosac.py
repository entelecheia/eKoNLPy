import pytest

from ekonlpy.sentiment.kosac import KOSAC

SKIPTAGS = ["SF", "SP", "SS", "SE", "SO", "SW", "UN", "UV", "UE", "OL", "OH", "ON"]


def _make_kosac():
    # KOSAC.__init__ requires konlpy (Kkma), which is not installed;
    # build the instance without the JVM-backed tagger.
    kosac = KOSAC.__new__(KOSAC)
    kosac._loaddic()
    kosac._ngram = 3
    kosac._delimiter = ";"
    kosac._skiptags = SKIPTAGS
    return kosac


def test_kosac_init_requires_konlpy():
    with pytest.raises(ImportError, match="Kkma"):
        KOSAC()


def test_loaddic_loads_all_lexicons():
    kosac = _make_kosac()

    assert "가*/JKS" in kosac._polarity
    assert "가*/JKS" in kosac._intensity
    assert "가*/JKS" in kosac._expressive


def test_align_morpheme_joins_surface_and_tag():
    kosac = _make_kosac()

    assert kosac.align_morpheme([("금리", "NNG"), ("인상", "NNG")]) == ["금리/NNG", "인상/NNG"]


def test_polarity_matches_dictionary_terms():
    kosac = _make_kosac()

    result = kosac.polarity(["가*/JKS"])

    assert result["pos"] == pytest.approx(1.0)
    assert sum(result.values()) == pytest.approx(1.0)


def test_intensity_matches_dictionary_terms():
    kosac = _make_kosac()

    result = kosac.intensity(["가*/JKS"])

    assert result["medium"] == pytest.approx(1.0)


def test_expressive_matches_dictionary_terms():
    kosac = _make_kosac()

    result = kosac.expressive(["가*/JKS"])

    assert result["dir-speech"] == pytest.approx(1.0)


def test_match_ignores_unknown_terms():
    kosac = _make_kosac()

    result = kosac.polarity(["가*/JKS", "알수없는토큰/NNG"])

    assert result["pos"] == pytest.approx(1.0)


def test_calc_applies_func_to_matching_keys():
    kosac = _make_kosac()
    keypairs = [["POS", "pos"], ["NEG", "neg"]]
    source = {"POS": "2"}
    target = {"pos": 1.0, "neg": 0.0}

    result = kosac.calc(keypairs, source, target, lambda s, t: t + s)

    assert result == {"pos": 3.0, "neg": 0.0}


def test_percentage_normalizes_values():
    kosac = _make_kosac()

    assert kosac.percentage({"a": 1.0, "b": 3.0}) == {"a": pytest.approx(0.25), "b": pytest.approx(0.75)}


def test_ngramize_skips_punctuation_tags_and_builds_ngrams():
    kosac = _make_kosac()

    tokens = kosac.ngramize(["금리/NNG", "./SF", "인상/NNG"])

    assert "금리/NNG" in tokens
    assert "인상/NNG" in tokens
    assert "금리/NNG;인상/NNG" in tokens
    assert all("./SF" not in token for token in tokens)


def test_ngramize_respects_max_ngram():
    kosac = _make_kosac()
    kosac._ngram = 1

    tokens = kosac.ngramize(["금리/NNG", "인상/NNG"])

    assert tokens == ["금리/NNG", "인상/NNG"]


def test_get_ngram_out_of_range_returns_none():
    kosac = _make_kosac()
    tokens = ["금리/NNG", "인상/NNG"]

    assert kosac.get_ngram(tokens, -1, 1) is None
    assert kosac.get_ngram(tokens, 1, 2) is None
    assert kosac.get_ngram(tokens, 0, 2) == "금리/NNG;인상/NNG"
