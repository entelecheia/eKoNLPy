# eKoNLPy: Korean NLP Python Library for Economic Analysis

[![pypi-image]][pypi-url]
[![version-image]][release-url]
[![release-date-image]][release-url]
[![pypi-downloads-image]][pypi-url]
[![license-image]][license-url]
[![codecov][codecov-image]][codecov-url]
[![zenodo-image]][zenodo-url]

<!-- Links: -->

[pypi-image]: https://badge.fury.io/py/ekonlpy.svg
[pypi-url]: https://badge.fury.io/py/ekonlpy
[license-image]: https://img.shields.io/github/license/entelecheia/eKoNLPy
[license-url]: https://github.com/entelecheia/eKoNLPy/blob/master/LICENSE
[version-image]: https://img.shields.io/github/v/release/entelecheia/eKoNLPy?sort=semver
[release-date-image]: https://img.shields.io/github/release-date/entelecheia/eKoNLPy
[release-url]: https://github.com/entelecheia/eKoNLPy/releases
[pypi-downloads-image]: https://img.shields.io/pypi/dm/ekonlpy
[codecov-image]: https://codecov.io/gh/entelecheia/eKoNLPy/branch/master/graph/badge.svg?token=8I4ORHRREL
[codecov-url]: https://codecov.io/gh/entelecheia/eKoNLPy
[zenodo-image]: https://zenodo.org/badge/DOI/10.5281/zenodo.7809447.svg
[zenodo-url]: https://doi.org/10.5281/zenodo.7809447

[repo-url]: https://github.com/entelecheia/eKoNLPy
[pypi-url]: https://pypi.org/project/ekonlpy
[docs-url]: https://ekonlpy.entelecheia.ai
[changelog]: https://github.com/entelecheia/eKoNLPy/blob/master/CHANGELOG.md
[contributing guidelines]: https://github.com/entelecheia/eKoNLPy/blob/master/CONTRIBUTING.md

<!-- Links: -->

`eKoNLPy` is a Korean Natural Language Processing (NLP) Python library specifically designed for economic analysis. It extends the functionality of the `MeCab` tagger from KoNLPy to improve the handling of economic terms, financial institutions, and company names, classifying them as single nouns. Additionally, it incorporates sentiment analysis features to determine the tone of monetary policy statements, such as Hawkish or Dovish.

**Important Note:**

eKoNLPy is built on the [fugashi](https://github.com/polm/fugashi) and [mecab-ko-dic](https://github.com/LuminosoInsight/mecab-ko-dic) libraries. For more information on using the `Mecab` tagger, please refer to the [fugashi documentation](https://github.com/polm/fugashi). As eKoNLPy no longer relies on the [KoNLPy](https://konlpy.org) library, Java is not required for its use. This makes eKoNLPy compatible with Windows, Linux, and Mac OS, without the need for Java installation. You can also use eKoNLPy on Google Colab.

If you wish to tokenize general Korean text with eKoNLPy, you do not need to install the `KoNLPy` library. Instead, utilize `ekonlpy.mecab.MeCab` as a replacement for `ekonlpy.tag.Mecab`.

However, if you plan to use the [Korean Sentiment Analyzer (KSA)](#korean-sentiment-analyzer-ksa), which employs the `Kkma` morpheme analyzer, you will need to install the [KoNLPy](https://konlpy.org) library.

## Installation

To install eKoNLPy, run the following command:

```bash
pip install ekonlpy
```

## Usage

### Part of Speech Tagging

To use the part of speech tagging feature, input `Mecab.pos(phrase)` just like KoNLPy. First, the input is processed using KoNLPy's Mecab morpheme analyzer. Then, if a combination of consecutive tokens matches a term in the user dictionary, the phrase is separated into compound nouns.

```python
from ekonlpy.tag import Mecab

mecab = Mecab()
mecab.pos('금통위는 따라서 물가안정과 병행, 경기상황에 유의하는 금리정책을 펼쳐나가기로 했다고 밝혔다.')
```

> [('금', 'MAJ'), ('통', 'MAG'), ('위', 'NNG'), ('는', 'JX'), ('따라서', 'MAJ'), ('물가', 'NNG'), ('안정', 'NNG'), ('과', 'JC'), ('병행', 'NNG'), (',', 'SC'), ('경기', 'NNG'), ('상황', 'NNG'), ('에', 'JKB'), ('유의', 'NNG'), ('하', 'XSV'), ('는', 'ETM'), ('금리', 'NNG'), ('정책', 'NNG'), ('을', 'JKO'), ('펼쳐', 'VV+EC'), ('나가', 'VX'), ('기', 'ETN'), ('로', 'JKB'), ('했', 'VV+EP'), ('다고', 'EC'), ('밝혔', 'VV+EP'), ('다', 'EF'), ('.', 'SF')]

### cf. MeCab POS Tagging (fugashi)

```python
from ekonlpy.mecab import MeCab # Be careful! `C` is capital.

mecab = MeCab()
mecab.pos('금통위는 따라서 물가안정과 병행, 경기상황에 유의하는 금리정책을 펼쳐나가기로 했다고 밝혔다.')
```

> [('금', 'MAJ'), ('통', 'MAG'), ('위', 'NNG'), ('는', 'JX'), ('따라서', 'MAJ'), ('물가', 'NNG'), ('안정', 'NNG'), ('과', 'JC'), ('병행', 'NNG'), (',', 'SC'), ('경기', 'NNG'), ('상황', 'NNG'), ('에', 'JKB'), ('유의', 'NNG'), ('하', 'XSV'), ('는', 'ETM'), ('금리', 'NNG'), ('정책', 'NNG'), ('을', 'JKO'), ('펼쳐', 'VV+EC'), ('나가', 'VX'), ('기', 'ETN'), ('로', 'JKB'), ('했', 'VV+EP'), ('다고', 'EC'), ('밝혔', 'VV+EP'), ('다', 'EF'), ('.', 'SF')]

### Lemmatization and Synonyms

To enhance the accuracy of sentiment analysis, eKoNLPy offers lemmatization and synonym handling features.

### Adding Words to Dictionary

You can add words to the dictionary in the `ekonlpy.tag` module's Mecab class, either as a string or a list of strings, using the `add_dictionary` method.

```python
from ekonlpy.tag import Mecab

mecab = Mecab()
mecab.add_dictionary('금통위', 'NNG')
```

## Sentiment Analysis

### Korean Monetary Policy Dictionary (MPKO)

To perform sentiment analysis using the Korean Monetary Policy dictionary, create an instance of the `MPKO` class in `ekonlpy.sentiment`:

```python
from ekonlpy.sentiment import MPKO

mpko = MPKO(kind=1)
tokens = mpko.tokenize(text)
score = mpko.get_score(tokens)
```

The `kind` parameter in the `MPKO` class is used to select a lexicon file:

- `0`: A lexicon file generated using a Naive-Bayes classifier with 5-gram tokens as features and changes of call rates as positive/negative labels.
- `1`: A lexicon file generated by polarity induction and seed propagation method with 5-gram tokens.

### Korean Monetary Policy Classifier (MPCK)

To use a classifier for monetary policy sentiment analysis, utilize the `MPCK` class from `ekonlpy.sentiment`:

```python
from ekonlpy.sentiment import MPCK

mpck = MPCK()
tokens = mpck.tokenize(text)
ngrams = mpck.ngramize(tokens)
score = mpck.classify(tokens + ngrams, intensity_cutoff=1.5)
```

You can set the `intensity_cutoff` parameter to adjust the intensity for classifying low-accuracy sentences as neutral (default: 1.3).

### Korean Sentiment Analyzer (KSA)

For general Korean sentiment analysis, use the `KSA` class. The morpheme analyzer used in this class is `Kkma` developed by Seoul National University's IDS Lab. The sentiment dictionary is also from the same lab (reference: http://kkma.snu.ac.kr/).

```python
from ekonlpy.sentiment import KSA

ksa = KSA()
tokens = ksa.tokenize(text)
score = ksa.get_score(tokens)
```

### Harvard IV-4 Dictionary

For general English sentiment analysis, use the Harvard IV-4 dictionary:

```python
from ekonlpy.sentiment import HIV4

hiv = HIV4()
tokens = hiv.tokenize(text)
score = hiv.get_score(tokens)
```

### Loughran and McDonald Dictionary

For sentiment analysis in the financial domain, use the Loughran and McDonald dictionary:

```python
from ekonlpy.sentiment import LM

lm = LM()
tokens = lm.tokenize(text)
score = lm.get_score(tokens)
```

## Changelog

See the [CHANGELOG] for more information.

## Contributing

Contributions are welcome! Please see the [contributing guidelines] for more information.

## License

eKoNLPy is an open-source software library for Korean Natural Language Processing (NLP), specifically designed for economic analysis. The library is released under the [MIT License][license-url], allowing developers and researchers to use, modify, and distribute the software as they see fit.

## Citation

If you use eKoNLPy in your work or research, please cite the following sources:

- Lee, Young Joon, eKoNLPy: A Korean NLP Python Library for Economic Analysis, 2018. Available at: https://github.com/entelecheia/eKoNLPy.
- Lee, Young Joon, Soohyon Kim, and Ki Young Park. "Deciphering Monetary Policy Board Minutes with Text Mining: The Case of South Korea." Korean Economic Review 35 (2019): 471-511.

You can also use the following BibTeX entry for citation:

```bibtex
@misc{lee2018ekonlpy,
    author= {Lee, Young Joon},
    year  = {2018},
    title = {{eKoNLPy: A Korean NLP Python Library for Economic Analysis}},
    note  = {\url{https://github.com/entelecheia/eKoNLPy}}
}
```

By citing eKoNLPy in your work, you acknowledge the efforts and contributions of its creators and help promote further development and research in the field of Korean NLP for economic analysis.
