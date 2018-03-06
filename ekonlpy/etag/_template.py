from ekonlpy.data.tagset import nochk_tags, chk_tags, skip_chk_tags, skip_tags


class ExTagger:
    def __init__(self, dictionary, max_tokens=5):
        self.dictionary = dictionary
        self.max_tokens = max_tokens
        self.nochk_tags = nochk_tags
        self.chk_tags = chk_tags
        self.skip_chk_tags = skip_chk_tags
        self.skip_tags = set(skip_tags)

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
        def ctagger(tokens, n, nochk_dic, chk_dic, skgrm_dic, skip_tags, term_dict):
            # tokens_org = [(p[0], 'NNG' if p[1] == 'NNP' else p[1]) for p in tokens]
            tokens_org = tokens
            tokens_new = []
            i = n - 1
            while i < len(tokens_org):

                tmp_tags = []
                for j in range(n):
                    tmp_tags.append('NNG'
                                    if tokens_org[i - n + j + 1][1] == 'NNP'
                                    else tokens_org[i - n + j + 1][1])
                tmp_tags = tuple(tmp_tags)

                if tmp_tags in nochk_dic.keys():
                    new_word = ''
                    for j in range(n):
                        new_word += tokens_org[i - n + j + 1][0]
                    new_tag = nochk_dic[tmp_tags]
                    tokens_new.append((new_word, new_tag))
                    i += n
                    continue
                elif tmp_tags in chk_dic.keys():
                    new_word = ''
                    for j in range(n):
                        new_word += tokens_org[i - n + j + 1][0]
                    dict_tag = term_dict.get_tags(new_word.lower())
                    if dict_tag:
                        new_tag = dict_tag if chk_dic[tmp_tags] == 'NNG' else chk_dic[tmp_tags]
                        tokens_new.append((new_word, new_tag))
                        i += n
                        continue
                elif tmp_tags in skgrm_dic.keys():
                    new_word = ''
                    for j in range(n):
                        if tmp_tags[j] not in skip_tags:
                            new_word += tokens_org[i - n + j + 1][0]
                    dict_tag = term_dict.get_tags(new_word.lower())
                    if dict_tag:
                        new_tag = dict_tag if chk_dic[tmp_tags] == 'NNG' else chk_dic[tmp_tags]
                        tokens_new.append((new_word, new_tag))
                        i += n
                        continue

                tokens_new.append(tokens_org[i - n + 1])

                if i == len(tokens_org) - 1:
                    for j in range(n - 1):
                        tokens_new.append(tokens_org[i - n + j + 2])
                i += 1

            return tokens_new

        for i in range(self.max_tokens, 1, -1):
            tokens = ctagger(tokens, i,
                                self.nochk_tags, self.chk_tags, self.skip_chk_tags,
                                self.skip_tags, self.dictionary)
        tokens = ctagger(tokens, 2,
                            self.nochk_tags, self.chk_tags, self.skip_chk_tags,
                            self.skip_tags, self.dictionary)

        return tokens
