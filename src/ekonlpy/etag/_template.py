from typing import Union

from ekonlpy.data.tagset import nouns_tags, pass_tags, skip_chk_tags, skip_tags
from ekonlpy.utils.dictionary import TermDictionary


class ExtTagger:
    """A template-based tagger that merges token n-grams into dictionary terms."""

    dictionary: TermDictionary
    max_ngram: int
    skip_chk_tags: dict[tuple[str, ...], str]
    skip_tags: set[str]
    nouns_tags: set[str]
    pass_tags: set[tuple[str, str]]

    def __init__(
        self,
        dictionary: TermDictionary,
        max_ngram: int = 7,
    ):
        """Initialize the tagger with a term dictionary and the tag templates.

        :param dictionary: The term dictionary to look up words in
        :param max_ngram: The maximum n-gram length to consider when merging tokens
        """
        self.dictionary = dictionary
        self.max_ngram = max_ngram
        self.skip_chk_tags = dict(skip_chk_tags)
        self.skip_tags = set(skip_tags)
        self.nouns_tags = set(nouns_tags)
        self.pass_tags = set(pass_tags)

    def add_skip_chk_tags(self, template: dict[tuple[str, ...], str]) -> None:
        """Add tag-sequence templates whose tokens are merged after skipping certain tags.

        :param template: Mapping of POS tag sequences to replacement tags
        """
        if isinstance(template, dict):
            self.skip_chk_tags.update(template)

    def add_skip_tags(self, tags: Union[list[str], set[str]]) -> None:
        """Add POS tags that are skipped when merging tokens.

        :param tags: The POS tags to skip
        """
        if isinstance(tags, (list, set)):
            self.skip_tags.update(tags)

    def pos(self, tokens: list[tuple[str, str]]) -> list[tuple[str, str]]:  # noqa: C901
        """Merge token n-grams matching the dictionary or templates into single terms.

        :param tokens: A list of (surface, pos) tuples
        :return: The re-tagged list of (surface, pos) tuples
        """

        def ctagger(  # noqa: C901
            ctokens: list[tuple[str, str]],
            max_ngram: int,
            cnouns_tags: set[str],
            cpass_tags: set[tuple[str, str]],
            cskip_chk_tags: dict[tuple[str, ...], str],
            cskip_tags: set[str],
            cdictionary: TermDictionary,
        ) -> list[tuple[str, str]]:
            """Merge n-grams in ctokens found in the dictionary or templates into single tokens."""
            tokens_org = ctokens
            num_tokens = len(ctokens)
            tokens_new: list[tuple[str, str]] = []
            ipos = 0

            while ipos < num_tokens:
                word_found = False
                for ngram in range(max_ngram, 1, -1):
                    # if found a word from the dictionary, skip for loop
                    if word_found or ipos + ngram > num_tokens:
                        continue
                    if any(
                        word.isspace() for word, _ in tokens_org[ipos : ipos + ngram]
                    ):
                        continue

                    tmp_tags = tuple(
                        (
                            "NNG"
                            if tokens_org[ipos + j][1] in cnouns_tags
                            else tokens_org[ipos + j][1]
                        )
                        for j in range(ngram)
                    )

                    if tmp_tags not in cpass_tags:
                        new_word = ""
                        for j in range(ngram):
                            new_word += tokens_org[ipos + j][0]
                        dict_tag = cdictionary.get_tags(new_word.lower())
                        if dict_tag:
                            tokens_new.append((new_word, dict_tag))
                            ipos += ngram
                            word_found = True

                    if not word_found and tmp_tags in cskip_chk_tags:
                        new_word = ""
                        num_word = ""
                        for j in range(ngram):
                            if tmp_tags[j] not in cskip_tags:
                                new_word += tokens_org[ipos + j][0]
                            num_word += (
                                "n" if tmp_tags[j] == "SN" else tokens_org[ipos + j][0]
                            )
                        dict_tag = cdictionary.get_tags(num_word.lower())
                        if dict_tag:
                            new_word = num_word
                        else:
                            dict_tag = cdictionary.get_tags(new_word.lower())
                        if dict_tag:
                            new_tag = (
                                dict_tag
                                if cskip_chk_tags[tmp_tags] == "NNG"
                                else cskip_chk_tags[tmp_tags]
                            )
                            tokens_new.append((new_word, new_tag))
                            ipos += ngram
                            word_found = True

                # if not found a word from the dictionary, add current token
                if not word_found:
                    tokens_new.append(tokens_org[ipos])
                    ipos += 1

            return tokens_new

        tokens = [
            (
                (w, t)
                if w.isspace()
                else (w.strip(), self.dictionary.check_tag(w.strip(), t))
            )
            for w, t in tokens
        ]

        tokens = ctagger(
            tokens,
            self.max_ngram,
            self.nouns_tags,
            self.pass_tags,
            self.skip_chk_tags,
            self.skip_tags,
            self.dictionary,
        )
        tokens = ctagger(
            tokens,
            3,
            self.nouns_tags,
            self.pass_tags,
            self.skip_chk_tags,
            self.skip_tags,
            self.dictionary,
        )

        tokens = [
            (w, t if w.isspace() else self.dictionary.check_tag(w, t))
            for w, t in tokens
        ]

        return tokens
