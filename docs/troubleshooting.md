# Troubleshooting

## MeCab dictionary errors

The standard installation includes `fugashi` and `mecab-ko-dic`. If `Mecab()`
reports that the dictionary is missing, check that the install completed in the
same environment as the Python process:

```bash
python -m pip show ekonlpy fugashi mecab-ko-dic
python -c "from ekonlpy import Mecab; print(Mecab().pos('한국은행'))"
```

When using a custom MeCab dictionary, pass its directory with `Mecab(dicdir=...)`.
For a compiled user dictionary, pass `userdic_path=...`.

## Notebook import mismatch

In Jupyter or Colab, use `%pip install ekonlpy` in a cell. `python -m pip` in a
separate terminal may install into a different interpreter. After changing an
already imported dependency, restart the kernel.

## KoNLPy and Java

The ordinary `Mecab`, `MPKO`, `EUKO`, `HIV4`, `LM`, and default `MPCK`
workflows do not require KoNLPy or Java. Install and configure KoNLPy for the
optional `KSA` or `KOSAC` classes, which use `konlpy.tag.Kkma`.

## MPCK custom model files

`MPCK.load_classifier(path)` expects a Python pickle containing an NLTK classifier.
Load only trusted files. A missing path raises `ValueError("There is no classifier file.")`.
The package's default model is loaded by `MPCK()`.

## Unexpected tagging

The default `Mecab()` applies the extended eKoNLPy vocabulary. Compare with
`Mecab(use_original_tagger=True)` when diagnosing a difference. Also check the
`fugashi` and `mecab-ko-dic` versions in the active environment. Use
`include_whitespace_token=True` when you need to inspect original whitespace;
spaces, tabs, and newlines are then returned as `SP` tokens.

## Vocabulary file errors

Synonym and lemma files use `word,value` rows. Blank and `#` comment lines are
allowed. A malformed nonempty row raises `ValueError` and identifies the file
and line number. Correct the source file and load it again; loading does not
rewrite the file.
