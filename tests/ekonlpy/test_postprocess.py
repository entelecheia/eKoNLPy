import pytest

from ekonlpy.tag import Mecab, Postprocessor

TEXT = "금통위는 따라서 물가안정과 병행, 경기상황에 유의하는 금리정책을 펼쳐나가기로 했다고 밝혔다."


@pytest.fixture()
def tagged():
    return Mecab().pos(TEXT)


def test_tag_without_filters_returns_base_output(tagged):
    post = Postprocessor(Mecab())

    assert post.tag(TEXT) == tagged


def test_stopwords_filter_by_surface_and_tuple(tagged):
    post = Postprocessor(Mecab(), stopwords=["따라서", ("금통위", "NNG")])

    tokens = post.tag(TEXT)

    assert "따라서" not in [w for w, _ in tokens]
    assert ("금통위", "NNG") not in tokens
    assert len(tokens) == len(tagged) - 2


def test_passwords_keep_only_listed_words():
    post = Postprocessor(Mecab(), passwords=["금통위", ("물가", "NNG")])

    tokens = post.tag(TEXT)

    assert tokens == [("금통위", "NNG"), ("물가", "NNG")]


def test_passtags_keep_only_listed_tags(tagged):
    post = Postprocessor(Mecab(), passtags=["NNG"])

    tokens = post.tag(TEXT)

    assert tokens == [w for w in tagged if w[1] == "NNG"]
    assert tokens


def test_replace_by_surface_keeps_tag(tagged):
    post = Postprocessor(Mecab(), replace={"금통위": "금융통화위원회"})

    tokens = post.tag(TEXT)

    assert ("금융통화위원회", "NNG") in tokens
    assert ("금통위", "NNG") not in tokens
    assert len(tokens) == len(tagged)


def test_replace_by_pair_with_pair_value():
    post = Postprocessor(
        Mecab(), replace={("금통위", "NNG"): ("금융통화위원회", "NNG")}
    )

    tokens = post.tag(TEXT)

    assert ("금융통화위원회", "NNG") in tokens


def test_unmatched_replace_leaves_tokens_unchanged(tagged):
    post = Postprocessor(Mecab(), replace={"없는단어": "대체"})

    assert post.tag(TEXT) == tagged


def test_combined_filters_apply_in_order(tagged):
    post = Postprocessor(
        Mecab(),
        stopwords=["따라서"],
        passtags=["NNG"],
        replace={"금통위": "금융통화위원회"},
    )

    tokens = post.tag(TEXT)

    expected = [
        ("금융통화위원회", "NNG") if w == ("금통위", "NNG") else w
        for w in tagged
        if w[1] == "NNG"
    ]
    assert tokens == expected
