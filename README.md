# eKoNLPy

[![PyPI](https://img.shields.io/pypi/v/ekonlpy.svg)](https://pypi.org/project/ekonlpy/)
[![License](https://img.shields.io/github/license/entelecheia/eKoNLPy)](https://github.com/entelecheia/eKoNLPy/blob/master/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-ekonlpy.entelecheia.ai-4c7)](https://ekonlpy.entelecheia.ai)

eKoNLPy is a Python library for Korean text processing in economic and financial
research. It provides a MeCab based tagger with an economic vocabulary and
lexicon based sentiment analyzers for Korean and English text.

This documentation follows the repository source, which may include unreleased
changes. Published versions are listed on [PyPI](https://pypi.org/project/ekonlpy/).

## Install

```bash
python -m pip install ekonlpy
```

eKoNLPy supports Python 3.9 or newer, below Python 4. The main CI matrix tests
Python 3.12-3.14 on Linux, macOS, and Windows, and Python 3.9-3.11 on Linux.
For Jupyter or Colab, install into the active kernel:

```python
%pip install ekonlpy
```

## Quick start

```python
from ekonlpy import Mecab

tagger = Mecab()
print(tagger.pos("금통위는 금리정책을 결정했다."))
```

The default tagger applies eKoNLPy's extended vocabulary. Use
`Mecab(use_original_tagger=True)` for the underlying fugashi/MeCab tagger.
Instances keep their dictionaries, synonyms, and lemmas separate from one
another. See the [documentation](https://ekonlpy.entelecheia.ai) for tagging,
custom vocabularies, sentiment analyzers, and the CLI.

## Sentiment example

```python
from ekonlpy.sentiment import MPKO

analyzer = MPKO(kind=1)
tokens = analyzer.tokenize("금리 인상이 필요하다")
print(analyzer.get_score(tokens))
```

The sentiment package also exports `EUKO`, `KSA`, `HIV4`, `LM`, and `MPCK`.
`KSA` uses KoNLPy's Java backed `Kkma` tokenizer and is optional. The separate
`KOSAC` analyzer is another optional KoNLPy integration.

## Development

```bash
make install
make check
make test
make docs-test
```

Contributions and issue reports are welcome on [GitHub](https://github.com/entelecheia/eKoNLPy).
For project documentation and verification steps, see the
[contributing guide](https://ekonlpy.entelecheia.ai/contributing/).

## License and citation

eKoNLPy is released under the [MIT License](LICENSE). Research users can cite
the project and the monetary policy text mining paper listed in the
[contributing and citation notes](https://ekonlpy.entelecheia.ai/contributing/).
