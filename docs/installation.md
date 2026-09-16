# Installation

## Python package

eKoNLPy requires Python `>=3.9,<4.0`:

```bash
python -m pip install ekonlpy
```

The package installs `fugashi` and `mecab-ko-dic`, so the standard `Mecab`
tagger does not require KoNLPy or a separate Java installation. The main CI
matrix tests Python 3.12-3.14 on Linux, macOS, and Windows, and Python 3.9-3.11
on Linux. These are the versions verified by the project; do not infer support
for an untested future interpreter.

Check the active installation:

```python
import platform
from importlib.metadata import version

import ekonlpy

print(platform.python_version())
print(version("ekonlpy"))
print(ekonlpy.Mecab().pos("한국은행"))
```

## Jupyter and Google Colab

Use `%pip` so the package goes into the kernel that runs the notebook:

```python
%pip install ekonlpy
```

Run the install cell before importing eKoNLPy. If an upgrade changes a package
already imported by the kernel, restart the kernel and run the notebook again
from its first setup cell.

## Optional KOSAC integration

`KSA` and the separate `KOSAC` class use `konlpy.tag.Kkma`; install KoNLPy and
its Java requirements only when you explicitly use either class:

```bash
python -m pip install konlpy
```

Follow KoNLPy's platform-specific Java setup instructions for Kkma. This optional
dependency is not needed for `Mecab`, `MPKO`, `EUKO`, `HIV4`, `LM`, or the
default `MPCK` workflow.
