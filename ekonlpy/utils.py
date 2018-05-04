import os

installpath = os.path.dirname(os.path.realpath(__file__))


def load_dictionary(fname, encoding='utf-8', rewrite=False):
    words = set()
    try:
        with open(fname, encoding=encoding) as f:
            words_ = {line.strip().lower() for line in f}
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


def save_wordlist(words, file_path):
    print('Save the list to the file: {}, no. of words: {}'.format(file_path, len(words)))
    with open(file_path, 'w') as f:
        for word in words:
            f.write(word + "\n")


def load_wordlist(file_path, rewrite=False, max_ngram=None,
                  remove_tag=False, sort=True, remove_delimiter=False):
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
    return words
