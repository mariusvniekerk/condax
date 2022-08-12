import logging
from typing import List

import click

import condax.config as config
import condax.core as core
from condax import __version__

from . import (
    cli,
    option_config,
    option_channels,
    option_is_forcing,
    option_channels,
    options_logging,
)


@cli.command(
    help=f"""
    Install a package with condax.

    This will install a package into a new conda environment and link the executable
    provided by it to `{config.DEFAULT_BIN_DIR}`.
    """
)
@option_channels
@option_config
@option_is_forcing
@options_logging
@click.argument("packages", nargs=-1)
def install(
    packages: List[str],
    is_forcing: bool,
    verbose: int,
    **_,
):
    for pkg in packages:
        core.install_package(
            pkg, is_forcing=is_forcing, conda_stdout=verbose <= logging.INFO
        )
