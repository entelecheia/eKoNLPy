from description import __version__, __author__
from setuptools import setup, find_packages

setup(
    name="eKoNLPy",
    version=__version__,
    author=__author__,
    author_email='yj.lee@yonsei.ac.kr',
    url='https://github.com/entelecheia/eKoNLPy',
    description="KoNLPy extended version (wrapping package)",
    long_description="""Add dictionary and tags and pos tagging with templates""",
    install_requires=["konlpy>=0.4.4"],
    keywords=['KoNLPy wrapping customization'],
    packages=find_packages(),
    package_data={'ekonlpy': ['data/*/*.txt']}
)
