import pytest

from ekonlpy.base import BaseMecab


class StubMecab(BaseMecab):
    def parse(self, text):
        return [("금리", "NNG"), ("인상", "NNG"), ("했다", "VV")]


def test_base_parse_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseMecab().parse("금리")


def test_base_pos_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseMecab().pos("금리")


def test_pos_delegates_to_parse():
    assert StubMecab().pos("text") == [("금리", "NNG"), ("인상", "NNG"), ("했다", "VV")]


def test_tokenize_with_pos_tags_and_custom_delimiter():
    tagger = StubMecab()

    assert tagger.tokenize("text") == ["금리/NNG", "인상/NNG", "했다/VV"]
    assert tagger.tokenize("text", postag_delim="^") == ["금리^NNG", "인상^NNG", "했다^VV"]
    assert tagger.tokenize("text", strip_pos=True) == ["금리", "인상", "했다"]


def test_morphs_strips_pos():
    assert StubMecab().morphs("text") == ["금리", "인상", "했다"]


def test_nouns_filters_by_pos():
    tagger = StubMecab()

    assert tagger.nouns("text", noun_pos=["NNG"]) == ["금리", "인상"]
    assert tagger.nouns("text") == []
