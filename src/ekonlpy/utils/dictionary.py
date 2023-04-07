from typing import Dict, List, Set, Union

term_tags = {
    "COUNTRY": "국가",
    "INDUSTRY": "산업용어",
    "NAME": "명칭",
    "SECTOR": "산업/업종",
    "ENTITY": "기업/종목",
    "GENERIC": "범용어",
    "GEO": "지역명",
    "CURRENCY": "화폐",
    "UNIT": "단위",
}


class TermDictionary:
    def __init__(self):
        self._pos2words: Dict[str, Set[str]] = {}

    def add_dictionary(self, words: Union[str, List[str]], tag: str) -> None:
        """
        Add a list of words or a single word to the dictionary under the given tag.

        :param words: Words to be added to the dictionary
        :param tag: Tag for the words being added
        """
        if isinstance(words, str):
            words = [words]
        wordset = self._pos2words.get(tag, set())
        wordset.update(set(words))
        self._pos2words[tag] = wordset

    def load_dictionary(self, fname: str, tag: str) -> None:
        """
        Load a dictionary from a file and add it under the given tag.

        :param fname: File name to load words from
        :param tag: Tag for the words being loaded
        """

        def load(filename: str) -> Set[str]:
            try:
                with open(filename, encoding="utf-8") as f:
                    words = {word.strip().lower() for word in f}
                    return words
            except Exception as e:
                print("load_dictionary error: %s" % e)
                return set()

        wordset = self._pos2words.get(tag, set())
        wordset.update(load(fname))
        self._pos2words[tag] = wordset

    def get_tags(self, word: str) -> str:
        """
        Get the tag associated with the given word.

        :param word: Word to get the tag for
        :return: The tag associated with the word
        """
        for tag, words in self._pos2words.items():
            if word.lower() in words:
                return tag

    def check_tag(self, word: str, tag: str) -> str:
        """
        Check and return the tag associated with the given word.

        :param word: Word to check the tag for
        :param tag: Initial tag to be checked against
        :return: The tag associated with the word
        """
        for tg, words in self._pos2words.items():
            if word.lower() in words:
                tag = tg
                break
        tag = tag.split("+")[0]
        tag = "NNG" if tag == "XR" else tag
        return tag

    def is_tag(self, word: str, tag: str) -> bool:
        """
        Check if the given word has the specified tag.

        :param word: Word to check the tag for
        :param tag: Tag to be checked against
        :return: True if the word has the specified tag, False otherwise
        """
        return word.lower() in self._pos2words.get(tag, {})

    def exists(self, word: str, tag: str = None) -> bool:
        """
        Check if the given word exists in the dictionary under the specified tag, or under any tag if no tag is given.

        :param word: Word to check
        :param tag: Tag to be checked against, or None to check all tags
        :return: True if the word exists in the dictionary under the specified tag or any tag, False otherwise
        """
        if tag in self._pos2words:
            return True if word.lower() in self._pos2words[tag] else False
        else:
            for tag, words in self._pos2words.items():
                if word.lower() in words:
                    return True
            return False
