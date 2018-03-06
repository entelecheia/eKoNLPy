import os

installpath = os.path.dirname(os.path.realpath(__file__))


def load_dictionary(fname, encoding='utf-8'):
    words = set()
    try:
        with open(fname, encoding=encoding) as f:
            words_ = {line.strip() for line in f}
            words.update(words_)
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
