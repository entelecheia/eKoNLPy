import os
from collections import OrderedDict
from typing import Dict, List, Set

installpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def load_dictionary(
    fname: str, encoding: str = "utf-8", rewrite: bool = False
) -> Set[str]:
    """
    Load words from a file and return a set of unique words.

    :param fname: File name to load words from
    :param encoding: Encoding of the file
    :param rewrite: If True, rewrite the file with unique words
    :return: Set of unique words
    """
    words = set()
    try:
        with open(fname, encoding=encoding) as f:
            words_ = {line.strip().lower().replace(" ", "") for line in f}
            words.update(words_)
        if rewrite:
            with open(fname, "w", encoding=encoding) as f:
                for word in words:
                    f.write(word + "\n")
    except Exception as e:
        print(e)

    return words


def load_txt(fname: str, encoding: str = "utf-8") -> List[str]:
    """
    Load lines from a text file and return a list of lines.

    :param fname: File name to load lines from
    :param encoding: Encoding of the file
    :return: List of lines
    """
    try:
        with open(fname, encoding=encoding) as f:
            return [line.strip() for line in f]
    except Exception as e:
        print(e)
        return []


def load_vocab(file_path: str, delimiter: str = ",") -> "OrderedDict[str, str]":
    """
    Load vocabulary from a file and return an ordered dictionary.

    :param file_path: File name to load vocabulary from
    :param delimiter: Delimiter used to separate words and their values
    :return: OrderedDict of vocabulary
    """
    vocab = OrderedDict()
    if os.path.isfile(file_path):
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                if delimiter in line:
                    w = line.strip().split(delimiter)
                    vocab[w[0].lower().replace(" ", "")] = w[1].lower().replace(" ", "")
                else:
                    save_vocab(vocab, file_path)
    vocab = OrderedDict((k, v) for k, v in sorted(vocab.items(), key=lambda x: x[0]))
    return vocab


def save_vocab(vocab: Dict[str, str], file_path: str, delimiter: str = ",") -> None:
    """
    Save vocabulary to a file.

    :param vocab: Dictionary of vocabulary to be saved
    :param file_path: File name to save vocabulary
    :param delimiter: Delimiter used to separate words and their values
    """
    vocab = [(w, c) for w, c in vocab.items()]
    with open(file_path, "w", encoding="utf-8") as f:
        for w, c in vocab:
            f.write(w + delimiter + str(c) + "\n")


def save_wordlist(words: List[str], file_path: str) -> None:
    """
    Save a list of words to a file.

    :param words: List of words to be saved
    :param file_path: File name to save the list of words
    """
    print(
        "Save the list to the file: {}, no. of words: {}".format(file_path, len(words))
    )
    with open(file_path, "w", encoding="utf-8") as f:
        for word in words:
            f.write(word + "\n")


def load_wordlist(
    file_path: str,
    rewrite: bool = False,
    max_ngram: int = None,
    remove_tag: bool = False,
    sort: bool = True,
    remove_delimiter: bool = False,
    lowercase: bool = False,
) -> List[str]:
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
    """
    words = []

    if os.path.isfile(file_path):
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

    if sort:
        words = sorted(set(words))
    else:
        words = set(words)

    print("Loaded the file: {}, No. of words: {}".format(file_path, len(words)))

    if rewrite:
        with open(file_path, "w", encoding="utf-8") as f:
            for word in words:
                f.write(word + "\n")
        print(
            "Saved the words to the file: {}, No. of words: {}".format(
                file_path, len(words)
            )
        )

    words = [word for word in words if not word.startswith("#")]
    words = [
        word.lower() if lowercase else word
        for word in words
        if not word.startswith("#")
    ]

    return words


def check_word_inclusion(
    word: str,
    check_list: List[str],
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
        if endswith:
            for check_word in check_list:
                if word.endswith(check_word.lower()):
                    return True
        elif startswith:
            for check_word in check_list:
                if word.startswith(check_word.lower()):
                    return True
        else:
            for check_word in check_list:
                if check_word.lower() in word:
                    return True
    return False
