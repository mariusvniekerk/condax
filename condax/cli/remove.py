import logging
from typing import List
import click

import condax.core as core
from condax import __version__

from . import cli, options_logging


@cli.command(
    help="""
    Remove a package.

    This will remove a package installed with condax and destroy the underlying
    conda environment.
    """
)
@options_logging
@click.argument("packages", nargs=-1)
def remove(packages: List[str], verbose: int, **_):
    for pkg in packages:
        core.remove_package(pkg, conda_stdout=verbose <= logging.INFO)


@cli.command(
    help="""
    Alias for condax remove.
    """
)
@options_logging
@click.argument("packages", nargs=-1)
def uninstall(packages: List[str], **_):
    remove(packages)
