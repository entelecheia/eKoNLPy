import pytest

from ekonlpy.utils.dictionary import TermDictionary
from ekonlpy.utils.io import load_dictionary, load_txt, load_vocab, load_wordlist


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
