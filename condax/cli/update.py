import logging
import sys
from typing import List

import click

import condax.core as core
from condax import __version__

from . import cli, options_logging


@cli.command(
    help="""
    Update package(s) installed by condax.

    This will update the underlying conda environments(s) to the latest release of a package.
    """
)
@click.option(
    "--all", is_flag=True, help="Set to update all packages installed by condax."
)
@click.option(
    "--update-specs", is_flag=True, help="Update based on provided specifications."
)
@options_logging
@click.argument("packages", required=False, nargs=-1)
@click.pass_context
def update(
    ctx: click.Context,
    all: bool,
    packages: List[str],
    update_specs: bool,
    verbose: int,
    **_
):
    if all:
        core.update_all_packages(update_specs)
    elif packages:
        for pkg in packages:
            core.update_package(pkg, update_specs, conda_stdout=verbose <= logging.INFO)
    else:
        ctx.fail("No packages specified.")
