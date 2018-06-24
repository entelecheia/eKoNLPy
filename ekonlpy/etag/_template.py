from ekonlpy.data.tagset import nochk_tags, chk_tags, skip_chk_tags, skip_tags, nouns_tags, \
    suffix_tags, xsav_tags, xsn_sfx_tag


class ExTagger:
    def __init__(self, dictionary, max_tokens=6):
        self.dictionary = dictionary
        self.max_tokens = max_tokens
        self.nochk_tags = nochk_tags
        self.suffix_tags = suffix_tags
        self.chk_tags = chk_tags
        self.skip_chk_tags = skip_chk_tags
        self.skip_tags = set(skip_tags)
        self.nouns_tags = nouns_tags
        self.xsav_tags = xsav_tags

    def add_nochk_tags(self, template):
        if type(template) == dict:
            self.nochk_tags.update(template)

    def add_chk_tags(self, template):
        if type(template) == dict:
            self.chk_tags.update(template)

    def add_skip_chk_tags(self, template):
        if type(template) == dict:
            self.skip_chk_tags.update(template)

    def add_skip_tags(self, tags):
        if type(tags) == list:
            self.skip_tags.update(tags)

    def pos(self, tokens):
        def ctagger(passes, tokens, n, nouns_tags, nochk_dic, chk_dic, skgrm_dic, xsav_tags,
                    skip_tags, suffix_tags, term_dict):
            # tokens_org = [(p[0], 'NNG' if p[1] == 'NNP' else p[1]) for p in tokens]
            tokens_org = tokens
            tokens_new = []
            i = n - 1
            # if length of tokens is less than n, bypass and return original tokens
            if len(tokens_org) < n:
                return tokens

            while i < len(tokens_org):
                tmp_tags = []
                for j in range(n):
                    tmp_tags.append('NNG'
                                    if tokens_org[i - n + j + 1][1] in nouns_tags
                                    else tokens_org[i - n + j + 1][1])
                tmp_tags = tuple(tmp_tags)

                if tmp_tags in chk_dic.keys():
                    new_word = ''
                    for j in range(n):
                        new_word += tokens_org[i - n + j + 1][0]
                    dict_tag = term_dict.get_tags(new_word.lower())
                    if dict_tag:
                        new_tag = dict_tag if chk_dic[tmp_tags] == 'NNG' else chk_dic[tmp_tags]
                        tokens_new.append((new_word, new_tag))
                        i += n
                        # if position of token reachs to the end, append remaining tokens
                        if i == len(tokens_org):
                            for j in range(n - 1):
                                tokens_new.append(tokens_org[i - n + j + 1])
                        continue

                if tmp_tags in skgrm_dic.keys():
                    new_word = ''
                    for j in range(n):
                        if tmp_tags[j] not in skip_tags:
                            new_word += tokens_org[i - n + j + 1][0]
                    dict_tag = term_dict.get_tags(new_word.lower())
                    if dict_tag:
                        new_tag = dict_tag if skgrm_dic[tmp_tags] == 'NNG' else skgrm_dic[tmp_tags]
                        tokens_new.append((new_word, new_tag))
                        i += n
                        # if position of token reachs to the end, append remaining tokens
                        if i == len(tokens_org):
                            for j in range(n - 1):
                                tokens_new.append(tokens_org[i - n + j + 1])
                        continue

                if passes > 0 and n == 2 and tmp_tags == xsn_sfx_tag:
                    # print(tokens_org[i - n + 1][0], tokens_org[i - n + 2][0])
                    for new_tag in suffix_tags.keys():
                        # print(len(tokens_org), i - n + 2)
                        if tokens_org[i - n + 2][0] in suffix_tags[new_tag]:
                            break
                    if tokens_org[i - n + 2][0] in suffix_tags[new_tag]:
                        new_word = tokens_org[i - n + 1][0] + tokens_org[i - n + 2][0]
                        tokens_new.append((new_word, new_tag))
                        i += n
                        # if position of token reachs to the end, append remaining tokens
                        if i == len(tokens_org):
                            for j in range(n - 1):
                                tokens_new.append(tokens_org[i - n + j + 1])
                        continue

                # if tmp_tags in nochk_dic.keys():
                #     new_word = ''
                #     for j in range(n):
                #         new_word += tokens_org[i - n + j + 1][0]
                #     new_tag = nochk_dic[tmp_tags]
                #     tokens_new.append((new_word, new_tag))
                #     i += n
                #     continue

                # if passes > 0 and n == 2 and tmp_tags in xsav_tags.keys():
                #     if tokens_org[i - n + 2][0][0] not in ['라']:
                #         new_word = tokens_org[i - n + 1][0] + tokens_org[i - n + 2][0]
                #         new_tag = xsav_tags[tmp_tags]
                #         tokens_new.append((new_word, new_tag))
                #         i += n
                #         # if position of token reachs to the end, append remaining tokens
                #         if i == len(tokens_org):
                #             for j in range(n - 1):
                #                 tokens_new.append(tokens_org[i - n + j + 1])
                #         continue

                tokens_new.append(tokens_org[i - n + 1])

                if i == len(tokens_org) - 1:
                    for j in range(n - 1):
                        tokens_new.append(tokens_org[i - n + j + 2])
                i += 1

            return tokens_new

        # tokens = [(w, self.dictionary.check_tag(w, t) if t in self.nouns_tags else t)
        tokens = [(w.strip(), self.dictionary.check_tag(w.strip(), t))
                  for w, t in tokens]

        for x in range(2):
            for t in range(self.max_tokens - x, 1, -1):
                tokens = ctagger(x, tokens, t,
                                 self.nouns_tags, self.nochk_tags, self.chk_tags, self.skip_chk_tags,
                                 self.xsav_tags, self.skip_tags, self.suffix_tags, self.dictionary,
                                 )
        # tokens = ctagger(tokens, 2,
        #                  self.nouns_tags, self.nochk_tags, self.chk_tags, self.skip_chk_tags,
        #                  self.xse_tags, self.skip_tags, self.suffix_tags, self.dictionary)
        tokens = [(w, self.dictionary.check_tag(w, t))
                  for w, t in tokens]

        return tokens
