from . import etag, tag
from ._version import __version__
from .utils.dictionary import TermDictionary
from .utils.io import installpath, load_dictionary, load_txt


def get_version() -> str:
    """This is the cli function of the package"""
    return __version__
