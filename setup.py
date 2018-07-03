from description import __title__, __version__, __author__, __author_email__, __description__, __url__, \
    __long_description__
from setuptools import setup, find_packages

setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    description=__description__,
    long_description=__long_description__,
    install_requires=['konlpy>=0.4.4', 'nltk >= 2.0'],
    keywords=['KoNLPy wrapping customization', 'Sentiment analysis', 'Monetary policy'],
    packages=find_packages(),
    package_data={'ekonlpy': ['data/*/*.txt', 'data/*/*.csv', 'data/*/*/*.csv', 'data/*/*/*.txt']}
)
