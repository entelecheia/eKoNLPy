# eKoNLPy

eKoNLPy is a Python library for Korean economic and financial text. It combines
a MeCab based Korean tagger with an economic vocabulary and six sentiment
exports: `MPKO`, `EUKO`, `KSA`, `HIV4`, `LM`, and `MPCK`.

## Start here

Install the package and run a tagger:

```bash
python -m pip install ekonlpy
```

```python
from ekonlpy import Mecab

tagger = Mecab()
tagger.pos("금통위는 금리정책을 결정했다.")
```

The default `Mecab` adds eKoNLPy's economic and entity vocabulary. Choose
`Mecab(use_original_tagger=True)` when you need the original fugashi/MeCab
tokenization path. Both return `(surface, part-of-speech)` pairs.

Use the guide that matches the task:

- [Installation](installation.md): supported Python versions, notebooks, and optional integrations.
- [Tagging](tagging.md): extended/original behavior, whitespace, nouns, and tokenization.
- [Dictionaries](dictionaries.md): user words, terms, synonyms, lemmas, and file formats.
- [Sentiment](sentiment.md): all six sentiment exports and their return values.
- [CLI reference](cli.md): the installed `ekonlpy` command and its actual options.
- [Troubleshooting](troubleshooting.md): MeCab, notebook, optional Java, and model issues.
- [Contributing and verification](contributing.md): local checks and documentation workflow.
