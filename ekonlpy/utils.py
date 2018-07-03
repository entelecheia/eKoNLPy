import os
from collections import OrderedDict

installpath = os.path.dirname(os.path.realpath(__file__))


def load_dictionary(fname, encoding='utf-8', rewrite=False):
    words = set()
    try:
        with open(fname, encoding=encoding) as f:
            words_ = {line.strip().lower().replace(' ', '') for line in f}
            words.update(words_)
        if rewrite:
            with open(fname, 'w') as f:
                for word in words:
                    f.write(word + "\n")

    except Exception as e:
        print(e)

    return words


def loadtxt(fname, encoding='utf-8'):
    try:
        with open(fname, encoding=encoding) as f:
            return [line.strip() for line in f]
    except Exception as e:
        print(e)
        return []


def load_vocab(file_path, delimiter=','):
    vocab = {}
    if os.path.isfile(file_path):
        with open(file_path) as f:
            for i, line in enumerate(f):
                if delimiter in line:
                    w = line.strip().split(delimiter)
                    vocab[w[0].lower().replace(' ', '')] = w[1].lower().replace(' ', '')
    else:
        save_vocab(vocab, file_path)
    # print('Loaded the file: {}, No. of words: {}'.format(file_path, len(vocab)))
    vocab = OrderedDict((k, v) for k, v in sorted(vocab.items(), key=lambda x: x[0]))
    return vocab


def save_vocab(vocab, file_path, delimiter=','):
    vocab = [(w, c) for w, c in vocab.items()]
    # print('Save the dict to the file: {}, No. of words: {}'.format(file_path, len(vocab)))
    with open(file_path, 'w') as f:
        for w, c in vocab:
            f.write(w + delimiter + str(c) + '\n')


def save_wordlist(words, file_path):
    print('Save the list to the file: {}, no. of words: {}'.format(file_path, len(words)))
    with open(file_path, 'w') as f:
        for word in words:
            f.write(word + "\n")


def load_wordlist(file_path, rewrite=False, max_ngram=None,
                  remove_tag=False, sort=True, remove_delimiter=False,
                  lowercase=False):
    if os.path.isfile(file_path):
        with open(file_path) as f:
            if remove_tag:
                words = [word.strip().split()[0].split('/')[0] for word in f if len(word.strip()) > 0]
            else:
                words = [word.strip().split()[0] for word in f if len(word.strip()) > 1]
    else:
        words = []
        save_wordlist(words, file_path)

    if remove_delimiter:
        words = [word.replace(';', '') for word in words]
    if max_ngram:
        words = [word for word in words if len(word.split(';')) <= max_ngram]
    if sort:
        words = sorted(set(words))
    else:
        words = set(words)
    print('Loaded the file: {}, No. of words: {}'.format(file_path, len(words)))
    if rewrite:
        with open(file_path, 'w') as f:
            for word in words:
                f.write(word + "\n")
        print('Saved the words to the file: {}, No. of words: {}'.format(file_path, len(words)))
    words = [word for word in words if not word.startswith('#')]
    words = [word.lower() if lowercase else word for word in words if not word.startswith('#')]
    return words


def check_word_inclusion(word, check_list, unit_level=False,
                         endswith=False, startswith=False):
    word = word.lower()
    if unit_level:
        if endswith:
            if word.split(';')[-1] in check_list:
                return True
        elif startswith:
            if word.split(';')[0] in check_list:
                return True
        else:
            for w in word.split(';'):
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
