import logging
import click

import condax.core as core
from condax import __version__

from . import cli, option_is_forcing, options_logging


@cli.command(
    help="""
    [experimental] Export all environments installed by condax.
    """
)
@click.option(
    "--dir",
    default="condax_exported",
    help="Set directory to export to.",
)
@options_logging
def export(dir: str, verbose: int, **_):
    core.export_all_environments(dir, conda_stdout=verbose <= logging.INFO)


@cli.command(
    "import",
    help="""
    [experimental] Import condax environments.
    """,
)
@option_is_forcing
@options_logging
@click.argument(
    "directory",
    required=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
def run_import(directory: str, is_forcing: bool, verbose: int, **_):
    core.import_environments(
        directory, is_forcing, conda_stdout=verbose <= logging.INFO
    )
