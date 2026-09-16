# Dictionaries

## Add words for one tagger

Use `add_dictionary` for words that should receive a MeCab tag. The tag must be
in the installed tag set unless `force=True` is intentional:

```python
from ekonlpy import Mecab

tagger = Mecab(use_default_dictionary=False)
tagger.add_dictionary(["금융위", "새별오름"], "NNP")
print(tagger.pos("금융위와 새별오름"))
```

`load_dictionary(path, tag)` reads one word per line. `add_terms` and
`load_terms` add words to the internal term categories used by `nouns` and
`sent_words`; their accepted categories include `COUNTRY`, `INDUSTRY`, `NAME`,
`SECTOR`, `ENTITY`, `GENERIC`, `CURRENCY`, and `UNIT`.

`use_default_dictionary=False` disables the bundled word loading, but the
tagger still initializes its synonym, lemma, and term-category resources. Use
the instance methods above to add or replace the entries relevant to a study.

## Synonyms and lemmas

Synonyms map a word to a replacement used by `replace_synonyms` and downstream
sentiment word extraction. Lemmas map an inflected form to its base form:

```python
tagger.add_synonym("한은", "한국은행")
tagger.add_lemma("올랐", "오르다")

print(tagger.replace_synonyms("한은"))
print(tagger.lemmatize([("올랐", "VV")]))
```

Use `load_synonyms(path, tag="NNG")` or `load_lemmas(path)` for files. Each
vocabulary row has two values separated by a comma, for example:

```text
한은,한국은행
인상했다,인상하다
```

Blank lines and lines beginning with `#` are skipped. A nonempty malformed row
raises `ValueError` with the file name and line number. Loading is read-only;
the input file is never rewritten. `persist_synonyms()` and `persist_lemmas()`
write the current maps to the package data directory, so use them only when you
intend to modify that installation.

## Instance isolation

Custom dictionaries, synonyms, lemmas, terms, and mutable tagger settings are
owned by each `Mecab` instance. Create a fresh instance for an independent
experiment or test.
