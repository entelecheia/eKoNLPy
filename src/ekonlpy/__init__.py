from . import etag, tag
from ._version import __version__
from .utils.dictionary import TermDictionary
from .utils.io import installpath, load_dictionary, load_txt


def get_version() -> str:
    """This function returns the version of ekonlpy."""
    return __version__
