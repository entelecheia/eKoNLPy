import logging
import os
from collections import OrderedDict
from typing import Optional

logger = logging.getLogger(__name__)

installpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def load_dictionary(
    fname: str, encoding: str = "utf-8", rewrite: bool = False
) -> set[str]:
    """
    Load words from a file and return a set of unique words.

    :param fname: File name to load words from
    :param encoding: Encoding of the file
    :param rewrite: If True, rewrite the file with unique words
    :return: Set of unique words
    :raises OSError: If the file cannot be read
    """
    with open(fname, encoding=encoding) as f:
        words = {line.strip().lower().replace(" ", "") for line in f if line.strip()}
    if rewrite:
        with open(fname, "w", encoding=encoding) as f:
            for word in words:
                f.write(word + "\n")
    return words


def load_txt(fname: str, encoding: str = "utf-8") -> list[str]:
    """
    Load lines from a text file and return a list of lines.

    :param fname: File name to load lines from
    :param encoding: Encoding of the file
    :return: List of lines
    :raises OSError: If the file cannot be read
    """
    with open(fname, encoding=encoding) as f:
        return [line.strip() for line in f]


def load_vocab(file_path: str, delimiter: str = ",") -> "OrderedDict[str, str]":
    """
    Load vocabulary without modifying the file, skipping blank lines and comments.

    Malformed nonempty rows raise ValueError with the file name and line number.

    :param file_path: File name to load vocabulary from
    :param delimiter: Delimiter used to separate words and their values
    :return: OrderedDict of vocabulary
    :raises OSError: If the file cannot be read
    """
    vocab = OrderedDict()
    with open(file_path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split(delimiter)
            if len(fields) < 2 or not fields[0].strip() or not fields[1].strip():
                raise ValueError(  # noqa: TRY003
                    f"Malformed vocabulary entry at {file_path}:{line_number}"
                )
            vocab[fields[0].lower().replace(" ", "")] = (
                fields[1].lower().replace(" ", "")
            )
    vocab = OrderedDict((k, v) for k, v in sorted(vocab.items(), key=lambda x: x[0]))
    return vocab


def save_vocab(vocab: dict[str, str], file_path: str, delimiter: str = ",") -> None:
    """
    Save vocabulary to a file.

    :param vocab: Dictionary of vocabulary to be saved
    :param file_path: File name to save vocabulary
    :param delimiter: Delimiter used to separate words and their values
    """
    items = list(vocab.items())
    with open(file_path, "w", encoding="utf-8") as f:
        for w, c in items:
            f.write(w + delimiter + str(c) + "\n")


def save_wordlist(words: list[str], file_path: str) -> None:
    """
    Save a list of words to a file.

    :param words: List of words to be saved
    :param file_path: File name to save the list of words
    """
    logger.info(
        "Save the list to the file: %s, no. of words: %d", file_path, len(words)
    )
    with open(file_path, "w", encoding="utf-8") as f:
        for word in words:
            f.write(word + "\n")


def load_wordlist(
    file_path: str,
    rewrite: bool = False,
    max_ngram: Optional[int] = None,
    remove_tag: bool = False,
    sort: bool = True,
    remove_delimiter: bool = False,
    lowercase: bool = False,
) -> list[str]:
    """
    Load a list of words from a file with various processing options.

    :param file_path: File name to load words from
    :param rewrite: If True, rewrite the file with the processed words
    :param max_ngram: Maximum n-gram size to keep in the list of words
    :param remove_tag: If True, remove tags from the words
    :param sort: If True, sort the list of words
    :param remove_delimiter: If True, remove delimiters from the words
    :param lowercase: If True, convert words to lowercase
    :return: List of processed words
    :raises OSError: If the file cannot be read
    """
    with open(file_path, encoding="utf-8") as f:
        if remove_tag:
            words = [
                word.strip().split()[0].split("/")[0]
                for word in f
                if len(word.strip()) > 0
            ]
        else:
            words = [word.strip().split()[0] for word in f if len(word.strip()) > 1]

    if remove_delimiter:
        words = [word.replace(";", "") for word in words]

    if max_ngram:
        words = [word for word in words if len(word.split(";")) <= max_ngram]

    words = sorted(set(words)) if sort else list(set(words))
    logger.info("Loaded the file: %s, No. of words: %d", file_path, len(words))

    if rewrite:
        with open(file_path, "w", encoding="utf-8") as f:
            for word in words:
                f.write(word + "\n")
        logger.info(
            "Saved the words to the file: %s, No. of words: %d", file_path, len(words)
        )

    words = [word for word in words if not word.startswith("#")]
    words = [
        word.lower() if lowercase else word
        for word in words
        if not word.startswith("#")
    ]

    return words


def check_word_inclusion(  # noqa: C901
    word: str,
    check_list: list[str],
    unit_level: bool = False,
    endswith: bool = False,
    startswith: bool = False,
) -> bool:
    """
    Check if a word is included in a list of words, based on given criteria.

    :param word: Word to check for inclusion
    :param check_list: List of words to check against
    :param unit_level: If True, check for inclusion at the unit level
    :param endswith: If True, check if the word ends with any of the words in the list
    :param startswith: If True, check if the word starts with any of the words in the list
    :return: True if the word meets the criteria, False otherwise
    """
    word = word.lower()

    if unit_level:
        if endswith:
            if word.split(";")[-1] in check_list:
                return True
        elif startswith:
            if word.split(";")[0] in check_list:
                return True
        else:
            for w in word.split(";"):
                if w in check_list:
                    return True
    else:
        for check_word in check_list:
            if endswith:
                if word.endswith(check_word.lower()):
                    return True
            elif startswith:
                if word.startswith(check_word.lower()):
                    return True
            elif check_word.lower() in word:
                return True
    return False
