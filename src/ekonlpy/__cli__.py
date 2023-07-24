"""Command line interface for eKoNLPy"""

# Importing the libraries

import click

from ._version import __version__

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
@click.option(
    "--tagger",
    "-t",
    show_default=True,
    default="ekonlpy",
    help="The tagger to use. [ekonlpy|mecab]]",
)
@click.option("--input", "-i", help="The input text to tag.")
@click.pass_context
def main(ctk, tagger, input):
    """This is the command line interface for eKoNLPy.

    It is used to tag Korean text with a Korean morphological analyzer.
    """
    # Print a message to the user.
    if input:
        click.echo(tag(tagger, input))
    else:
        # Print usage message to the user.
        click.echo(ctk.get_help())


def tag(tagger: str, text: str) -> list:
    from ekonlpy import Mecab

    mecab = Mecab(use_original_tagger=tagger == "mecab")
    return mecab.pos(text)


# main function for the main module
if __name__ == "__main__":
    main()
