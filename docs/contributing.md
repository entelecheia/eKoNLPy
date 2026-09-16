# Contributing and verification

## Local setup

The repository uses `uv` and a Python 3.12 development interpreter:

```bash
make install
```

Run the primary checks before opening a pull request:

```bash
make check && make test
```

`make docs-test` builds the site with strict warning handling. Keep examples
limited to APIs that exist in the current source and run new Python snippets in
the repository environment when practical:

```bash
.venv/bin/python -c "from ekonlpy import Mecab; print(Mecab().pos('한국은행'))"
```

For source changes, also run `make check`. The CI matrix covers Python 3.9-3.14
as described in [Installation](installation.md), with the broader operating
system coverage on Python 3.12-3.14.

## Documentation changes

Put user-facing behavior in the page that describes it and add a nav entry in
`mkdocs.yaml` for new pages. Do not describe a release as published unless it
is verifiable on PyPI.

## Citation

If you use eKoNLPy in research, cite:

```text
Lee, Young Joon. eKoNLPy: A Korean NLP Python Library for Economic Analysis. 2018.
https://github.com/entelecheia/eKoNLPy
```

For monetary policy text mining, also see:

```text
Lee, Young Joon, Soohyon Kim, and Ki Young Park. "Deciphering Monetary Policy
Board Minutes with Text Mining: The Case of South Korea." Korean Economic Review
35 (2019): 471-511.
```

Questions and contributions can be opened on the
[GitHub repository](https://github.com/entelecheia/eKoNLPy).
