import click

import condax.config as config
import condax.conda as conda
import condax.core as core
import condax.migrate as migrate
from condax import __version__

from . import cli, options_logging


@cli.command(
    help=f"""
    [experimental] Repair condax links in BIN_DIR.

    By default BIN_DIR is {config.DEFAULT_BIN_DIR}.
    """
)
@click.option(
    "--migrate",
    "is_migrating",
    help="""Migrate from the original condax version.""",
    is_flag=True,
    default=False,
)
@options_logging
def repair(is_migrating, **_):
    if is_migrating:
        migrate.from_old_version()
    conda.setup_micromamba()
    core.fix_links()
