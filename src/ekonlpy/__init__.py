from ._version import __version__
from .mecab import MecabDicConfig
from .tag import Mecab
from .utils.dictionary import TermDictionary
from .utils.io import installpath


def get_version() -> str:
    """This function returns the version of ekonlpy."""
    return __version__


__all__ = [
    "Mecab",
    "MecabDicConfig",
    "TermDictionary",
    "installpath",
    "get_version",
]
