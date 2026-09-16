import pytest

from ekonlpy import Mecab, TermDictionary
from ekonlpy.etag import ExtTagger
from ekonlpy.utils.io import load_vocab


def test_analyzers_do_not_share_user_state():
    first = Mecab(use_default_dictionary=False)
    second = Mecab(use_default_dictionary=False)
    before = second.pos("실습")
    first.add_dictionary("실습", "NNP")
    first.add_synonym("임시용어", "대체용어")
    first.add_lemma("테스트했다", "테스트하다")
    first.stopwords.append("실습")
    first.tagset["NNG"] = "changed"
    first._terms.add_dictionary("임시분야", "SECTOR")
    first._extagger.add_skip_chk_tags({("CUSTOM",): "NNP"})
    assert first.pos("실습") == [("실습", "NNP")]
    for other in (second, Mecab(use_default_dictionary=False)):
        assert other.pos("실습") == before
        assert other.replace_synonyms([("임시용어", "NNG")]) == [("임시용어", "NNG")]
        assert "테스트했다" not in other._lemmas
        assert "실습" not in other.stopwords
        assert other.tagset["NNG"] != "changed"
        assert not other._terms.exists("임시분야")
        assert ("CUSTOM",) not in other._extagger.skip_chk_tags


def test_original_analyzer_does_not_inherit_extended_state():
    extended = Mecab()
    extended.add_dictionary("실습", "NNP")
    original = Mecab(use_original_tagger=True)
    assert original.pos("실습") == [("실습", "NNG")]
    assert original._extagger is None
    assert original._dictionary.get_tags("실습") is None


@pytest.mark.parametrize("suffix", [[], [(".", "SF")]])
def test_compound_at_end_of_sentence(suffix):
    dictionary = TermDictionary()
    dictionary.add_dictionary("새별오름", "NNP")
    tagger = ExtTagger(dictionary)
    assert tagger.pos([("새별", "NNG"), ("오름", "NNG"), *suffix]) == [("새별오름", "NNP"), *suffix]


def test_preserved_whitespace_is_a_compound_boundary():
    dictionary = TermDictionary()
    dictionary.add_dictionary("새별오름", "NNP")
    tokens = [("새별", "NNG"), (" \t", "SP"), ("오름", "NNG")]
    assert ExtTagger(dictionary).pos(tokens) == tokens


@pytest.mark.parametrize("original", [True, False])
@pytest.mark.parametrize("flatten", [True, False])
@pytest.mark.parametrize("text", ["", " \t\n", "나는 성산으로 갔다", "  나는\t갔다\n", "갔다  갔다 "])
def test_whitespace_runs_survive_tagging(original, flatten, text):
    import re

    tagger = Mecab(use_original_tagger=original)
    tokens = tagger.pos(text, flatten=flatten, include_whitespace_token=True)
    assert [word for word, _ in tokens if word.isspace()] == re.findall(r"\s+", text)
    assert all(tag == "SP" for word, tag in tokens if word.isspace())
    assert [(word, tag) for word, tag in tokens if not word.isspace()] == tagger.pos(text, flatten=flatten)
    if original and flatten:
        assert "".join(word for word, _ in tokens) == text


def test_load_vocab_is_read_only(tmp_path):
    path = tmp_path / "vocab.txt"
    contents = "하나,첫째\n\n# comment\n둘,둘째\n"
    path.write_text(contents, encoding="utf-8")
    assert dict(load_vocab(str(path))) == {"하나": "첫째", "둘": "둘째"}
    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize("row", ["malformed", ",value", "key,"])
def test_malformed_vocab_reports_location_without_truncating(tmp_path, row):
    path = tmp_path / "vocab.txt"
    contents = f"하나,첫째\n{row}\n둘,둘째\n"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(ValueError, match=r"vocab\.txt:2"):
        load_vocab(str(path))
    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize("from_file", [False, True])
def test_term_categories_filter_words_without_changing_pos(tmp_path, from_file):
    tagger = Mecab(use_default_dictionary=False)
    other = Mecab(use_default_dictionary=False)
    original = tagger.pos("실습")
    if from_file:
        path = tmp_path / "terms.txt"
        path.write_text("실습\n", encoding="utf-8")
        tagger.load_terms(str(path), "SECTOR")
    else:
        tagger.add_terms(["실습"], "SECTOR")
    assert tagger.pos("실습") == original
    assert tagger.nouns("실습") == []
    assert tagger.nouns("실습", include_sector_name=True) == ["실습"]
    assert other.nouns("실습") == ["실습"]
