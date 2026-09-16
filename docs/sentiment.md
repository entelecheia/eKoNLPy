# Sentiment analysis

The sentiment classes tokenize text and score a list of tokens. A typical
workflow is:

```python
from ekonlpy.sentiment import MPKO

analyzer = MPKO(kind=1)
tokens = analyzer.tokenize("금리 인상이 필요하다")
result = analyzer.get_score(tokens)
print(result)
```

`get_score` returns `Positive`, `Negative`, `Polarity`, and `Subjectivity`.
Pass `return_breakdown=True` to include one record per input term. For `MPKO`
and `EUKO`, `by_count=False` uses the polarity values in their lexicons:

```python
from ekonlpy.sentiment import MPKO

analyzer = MPKO(kind=1)
tokens = analyzer.tokenize("금리 인상이 필요하다")
print(analyzer.get_score(tokens, return_breakdown=True))
print(analyzer.get_phrase_breakdown(tokens))
```

`HIV4` and `LM` classify terms by occurrence. Their bundled implementations do
not populate `_poldict`, so `by_count=False` produces zero weighted scores for
those classes; use the default `by_count=True` mode.

## Exported analyzers

| Class | Text and lexicon | Notes |
| --- | --- | --- |
| `MPKO` | Korean monetary policy | `kind` selects the bundled policy lexicon. Supported kinds are `0`, `1`, `3`, and `7`. Positive means hawkish and negative means dovish. |
| `EUKO` | Korean economic uncertainty | Scores terms from the bundled uncertainty lexicon. |
| `KSA` | Korean general sentiment | Bundled KOSAC polarity dictionary with KoNLPy's `Kkma` tokenizer. Requires the optional Java backed KoNLPy integration. |
| `HIV4` | English general sentiment | Harvard IV-4 terms are stemmed by the default tokenizer. |
| `LM` | English financial sentiment | Loughran and McDonald terms are stemmed by the default tokenizer. |
| `MPCK` | Korean monetary policy classifier | Uses the bundled NLTK Naive Bayes model and MeCab tokenization. |

All six are importable from `ekonlpy.sentiment`:

```python
from ekonlpy.sentiment import EUKO, HIV4, KSA, LM, MPCK, MPKO
```

## Korean and English dictionary analyzers

`EUKO` scores Korean economic uncertainty terms. It supports `kind=0` and
`kind=1`:

```python
from ekonlpy.sentiment import EUKO

analyzer = EUKO(kind=1)
tokens = analyzer.tokenize("금리 인상이 필요하다")
print(tokens)
print(analyzer.get_score(tokens))
```

`HIV4` and `LM` use an English tokenizer with Porter stemming:

```python
from ekonlpy.sentiment import HIV4, LM

for analyzer in (HIV4(), LM()):
    tokens = analyzer.tokenize("abundance and abandon")
    print(type(analyzer).__name__, tokens, analyzer.get_score(tokens))
```

## MPCK classification

`MPCK` uses its bundled classifier by default:

```python
from ekonlpy.sentiment import MPCK

classifier = MPCK()
tokens = classifier.tokenize("금리 인상이 필요하다")
features = tokens + classifier.ngramize(tokens)
print(classifier.classify(features, intensity_cutoff=1.3))
```

The result contains `Polarity`, `Intensity`, `Pos score`, and `Neg score`.
`load_classifier` and `save_classifier` read and write Python pickle files.
Only load a model file you trust: unpickling can execute arbitrary code. The
bundled model is loaded automatically; custom model files are an advanced,
trusted-input workflow.

## Optional KSA and KOSAC analyzers

`KSA` uses the bundled KOSAC polarity dictionary with KoNLPy's Java backed
`Kkma` tokenizer. `KOSAC` is a separate analyzer that also uses `Kkma`. Install
and configure the optional KoNLPy and Java dependencies before constructing
either class:

```python
from ekonlpy.sentiment import KSA

analyzer = KSA()
tokens = analyzer.tokenize("좋은 정책")
print(analyzer.get_score(tokens))
```

This optional example is not executed in the project's default development
environment because KoNLPy and Java are not installed there.
