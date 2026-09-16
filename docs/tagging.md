# Tagging

## Extended and original taggers

`ekonlpy.Mecab` is the public tagger. By default it post-processes fugashi
output with eKoNLPy's economic, institution, entity, and other bundled
dictionaries:

```python
from ekonlpy import Mecab

extended = Mecab()
original = Mecab(use_original_tagger=True)

print(extended.pos("금통위는 금리정책을 결정했다."))
print(original.pos("금통위는 금리정책을 결정했다."))
```

`pos(text, flatten=True, include_whitespace_token=False)` returns a list of
`(surface, tag)` pairs. `flatten=False` preserves MeCab inflection components
where the backend provides them. `morphs(text)` returns surfaces only, and
`nouns(text)` returns noun surfaces.

When `include_whitespace_token=True`, each original whitespace run is returned
as an `SP` token. This includes leading and trailing spaces, tabs, and newlines.
Whitespace is kept separate from compound matching.

```python
tagger = Mecab(use_default_dictionary=False)
print(tagger.pos("  가\t나\n", include_whitespace_token=True))
```

## Nouns, synonyms, and lemmas

The extended tagger can normalize text before extracting research terms:

```python
tagger = Mecab(use_default_dictionary=False)
tagger.add_dictionary("새별오름", "NNP")
tagger.add_synonym("물가안정", "물가 안정")
tagger.add_lemma("올랐", "오르다")

print(tagger.nouns("새별오름과 물가안정을 검토했다."))
print(tagger.replace_synonyms("물가안정"))
print(tagger.lemmatize([("올랐", "VV")]))
```

Each `Mecab` instance owns these mutable dictionaries. Changes made to one
instance do not alter another instance.

## Token strings

`tokenize` returns strings in `surface/tag` form by default. Set `strip_pos=True`
to return surfaces only:

```python
print(tagger.tokenize("금리정책", strip_pos=False))
print(tagger.tokenize("금리정책", strip_pos=True))
```

For dictionary loading and persistence, see [Dictionaries](dictionaries.md).
