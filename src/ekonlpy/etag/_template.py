from ..data.tagset import nouns_tags, pass_tags, skip_chk_tags, skip_tags


class ExtTagger:
    def __init__(self, dictionary, max_ngram=7):
        self.dictionary = dictionary
        self.max_ngram = max_ngram
        self.skip_chk_tags = skip_chk_tags
        self.skip_tags = set(skip_tags)
        self.nouns_tags = set(nouns_tags)
        self.pass_tags = set(pass_tags)

    def add_skip_chk_tags(self, template):
        if type(template) == dict:
            self.skip_chk_tags.update(template)

    def add_skip_tags(self, tags):
        if type(tags) == list:
            self.skip_tags.update(tags)

    def pos(self, tokens):
        def ctagger(
            ctokens,
            max_ngram,
            cnouns_tags,
            cpass_tags,
            cskip_chk_tags,
            cskip_tags,
            cdictionary,
        ):
            tokens_org = ctokens
            num_tokens = len(ctokens)
            tokens_new = []
            ipos = 0

            while ipos < num_tokens:
                word_found = False
                for ngram in range(max_ngram, 1, -1):
                    # if found a word from the dictionary, skip for loop
                    if word_found or ipos + ngram > num_tokens - 1:
                        continue

                    tmp_tags = []
                    for j in range(ngram):
                        tmp_tags.append(
                            "NNG"
                            if tokens_org[ipos + j][1] in cnouns_tags
                            else tokens_org[ipos + j][1]
                        )
                    tmp_tags = tuple(tmp_tags)

                    if tmp_tags not in cpass_tags:
                        new_word = ""
                        for j in range(ngram):
                            new_word += tokens_org[ipos + j][0]
                        dict_tag = cdictionary.get_tags(new_word.lower())
                        if dict_tag:
                            tokens_new.append((new_word, dict_tag))
                            ipos += ngram
                            word_found = True

                    if not word_found and tmp_tags in cskip_chk_tags.keys():
                        new_word = ""
                        num_word = ""
                        for j in range(ngram):
                            if tmp_tags[j] not in cskip_tags:
                                new_word += tokens_org[ipos + j][0]
                            if tmp_tags[j] == "SN":
                                num_word += "n"
                            else:
                                num_word += tokens_org[ipos + j][0]
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
            (w.strip(), self.dictionary.check_tag(w.strip(), t)) for w, t in tokens
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

        tokens = [(w, self.dictionary.check_tag(w, t)) for w, t in tokens]

        return tokens
