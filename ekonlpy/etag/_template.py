from ekonlpy.data.tagset import skip_chk_tags, skip_tags, nouns_tags, pass_tags


class ETagger:
    def __init__(self, dictionary, max_ngram=6):
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
        def ctagger(ctokens, ngram, cnouns_tags, cpass_tags, cskip_chk_tags, cskip_tags, cdictionary):

            tokens_org = ctokens
            num_tokens = len(ctokens)
            tokens_new = []
            i = ngram - 1
            # if length of tokens is less than n, bypass and return original tokens
            if num_tokens < ngram:
                return ctokens

            while i < num_tokens:
                tmp_tags = []
                for j in range(ngram):
                    tmp_tags.append('NNG'
                                    if tokens_org[i - ngram + j + 1][1] in cnouns_tags
                                    else tokens_org[i - ngram + j + 1][1])
                tmp_tags = tuple(tmp_tags)

                if tmp_tags not in cpass_tags:
                    new_word = ''
                    for j in range(ngram):
                        new_word += tokens_org[i - ngram + j + 1][0]
                    dict_tag = cdictionary.get_tags(new_word.lower())
                    if dict_tag:
                        tokens_new.append((new_word, dict_tag))
                        i += ngram
                        # if position of token reachs to the end, append remaining tokens
                        if i >= num_tokens:
                            for j in range(ngram - 1):
                                pos = i - ngram + j + 1
                                if pos < num_tokens:
                                    tokens_new.append(tokens_org[pos])
                        continue

                if tmp_tags in cskip_chk_tags.keys():
                    new_word = ''
                    num_word = ''
                    for j in range(ngram):
                        if tmp_tags[j] not in cskip_tags:
                            new_word += tokens_org[i - ngram + j + 1][0]
                        if tmp_tags[j] == 'SN':
                            num_word += 'n'
                        else:
                            num_word += tokens_org[i - ngram + j + 1][0]
                    dict_tag = cdictionary.get_tags(num_word.lower())
                    if dict_tag:
                        new_word = num_word
                    else:
                        dict_tag = cdictionary.get_tags(new_word.lower())
                    if dict_tag:
                        new_tag = dict_tag if cskip_chk_tags[tmp_tags] == 'NNG' else cskip_chk_tags[tmp_tags]
                        tokens_new.append((new_word, new_tag))
                        i += ngram
                        # if position of token reachs to the end, append remaining tokens
                        if i >= num_tokens:
                            for j in range(ngram - 1):
                                pos = i - ngram + j + 1
                                if pos < num_tokens:
                                    tokens_new.append(tokens_org[pos])
                        continue

                tokens_new.append(tokens_org[i - ngram + 1])
                # if position of token reachs to the end, append remaining tokens
                if i >= num_tokens - 1:
                    for j in range(ngram - 1):
                        pos = i - ngram + j + 2
                        if pos < num_tokens:
                            tokens_new.append(tokens_org[pos])
                i += 1

            return tokens_new

        tokens = [(w.strip(), self.dictionary.check_tag(w.strip(), t))
                  for w, t in tokens]

        for x in range(2):
            for t in range(self.max_ngram - x, 1, -1):
                tokens = ctagger(tokens, t, self.nouns_tags, self.pass_tags,
                                 self.skip_chk_tags, self.skip_tags, self.dictionary)

        tokens = [(w, self.dictionary.check_tag(w, t))
                  for w, t in tokens]

        return tokens
