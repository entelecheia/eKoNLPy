import pytest

from ekonlpy.utils.dictionary import TermDictionary
from ekonlpy.utils.io import (
    check_word_inclusion,
    load_dictionary,
    load_txt,
    load_vocab,
    load_wordlist,
    save_vocab,
    save_wordlist,
)


def test_loaders_raise_for_missing_file(tmp_path):
    missing = str(tmp_path / "missing.txt")

    with pytest.raises(FileNotFoundError):
        load_dictionary(missing)
    with pytest.raises(FileNotFoundError):
        load_txt(missing)
    with pytest.raises(FileNotFoundError):
        load_vocab(missing)
    with pytest.raises(FileNotFoundError):
        load_wordlist(missing)


def test_term_dictionary_load_raises_for_missing_file(tmp_path):
    terms = TermDictionary()

    with pytest.raises(FileNotFoundError):
        terms.load_dictionary(str(tmp_path / "missing.txt"), "NNG")


def test_load_dictionary_skips_blank_lines(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("사과\n\n  \n배\n", encoding="utf-8")

    words = load_dictionary(str(path))

    assert words == {"사과", "배"}
    assert "" not in words


def test_term_dictionary_load_skips_blank_lines(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("사과\n\n배\n", encoding="utf-8")
    terms = TermDictionary()
    terms.load_dictionary(str(path), "NNG")

    assert not terms.exists("")


def test_load_vocab_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_vocab(str(tmp_path / "missing.txt"))


def test_load_vocab_malformed_row_names_file_and_line(tmp_path):
    path = tmp_path / "vocab.txt"
    path.write_text("good,1\n\nbad\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"vocab\.txt:3"):
        load_vocab(str(path))


def test_load_wordlist_logs_instead_of_printing(tmp_path, capsys):
    path = tmp_path / "words.txt"
    path.write_text("사과\n배추\n", encoding="utf-8")

    words = load_wordlist(str(path))

    assert sorted(words) == ["배추", "사과"]
    assert capsys.readouterr().out == ""


def test_save_vocab_round_trip(tmp_path):
    path = tmp_path / "vocab.txt"
    vocab = {"사과": "1", "배": "2"}

    save_vocab(vocab, str(path))

    assert dict(load_vocab(str(path))) == vocab


def test_save_wordlist_round_trip(tmp_path):
    path = tmp_path / "words.txt"

    save_wordlist(["사과", "배추"], str(path))

    assert load_wordlist(str(path)) == ["배추", "사과"]


def test_load_wordlist_remove_tag(tmp_path):
    path = tmp_path / "tagged.txt"
    path.write_text("사과/NNG 1\n배/NNP\n", encoding="utf-8")

    assert load_wordlist(str(path), remove_tag=True) == ["배", "사과"]


def test_load_wordlist_remove_delimiter_and_max_ngram(tmp_path):
    path = tmp_path / "ngrams.txt"
    path.write_text("금리;인상\n금리\n", encoding="utf-8")

    assert load_wordlist(str(path), remove_delimiter=True) == ["금리", "금리인상"]
    assert load_wordlist(str(path), max_ngram=1) == ["금리"]
    assert load_wordlist(str(path), max_ngram=2) == ["금리", "금리;인상"]


def test_load_wordlist_skips_single_char_lines(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("가\n사과\n", encoding="utf-8")

    assert load_wordlist(str(path)) == ["사과"]


def test_load_wordlist_lowercase_and_unsorted(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("ABC\nDef\n", encoding="utf-8")

    assert load_wordlist(str(path), lowercase=True) == ["abc", "def"]
    assert set(load_wordlist(str(path), sort=False)) == {"ABC", "Def"}


def test_load_wordlist_filters_comment_lines(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("# 주석\n사과\n", encoding="utf-8")

    assert load_wordlist(str(path)) == ["사과"]


def test_load_wordlist_rewrite_updates_file(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("배추\n사과\n사과\n", encoding="utf-8")

    words = load_wordlist(str(path), rewrite=True)

    assert words == ["배추", "사과"]
    assert path.read_text(encoding="utf-8").splitlines() == ["배추", "사과"]


@pytest.mark.parametrize(
    ("word", "check_list", "options", "expected"),
    [
        ("금리;인상", ["인상"], {"unit_level": True, "endswith": True}, True),
        ("금리;인상", ["금리"], {"unit_level": True, "endswith": True}, False),
        ("금리;인상", ["금리"], {"unit_level": True, "startswith": True}, True),
        ("금리;인상", ["인상"], {"unit_level": True, "startswith": True}, False),
        ("금리;인상", ["인상"], {"unit_level": True}, True),
        ("금리;인상", ["하락"], {"unit_level": True}, False),
        ("금리인상", ["인상"], {"endswith": True}, True),
        ("금리인상", ["금리"], {"endswith": True}, False),
        ("금리인상", ["금리"], {"startswith": True}, True),
        ("금리인상", ["인상"], {"startswith": True}, False),
        ("금리인상", ["인상"], {}, True),
        ("금리인상", ["하락"], {}, False),
    ],
)
def test_check_word_inclusion_option_combinations(word, check_list, options, expected):
    assert check_word_inclusion(word, check_list, **options) is expected
