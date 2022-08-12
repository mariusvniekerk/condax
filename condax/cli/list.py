import click

import condax.core as core
from condax import __version__

from . import cli, options_logging


@cli.command(
    "list",
    help="""
    List packages managed by condax.

    This will show all packages installed by condax.
    """,
)
@click.option(
    "-s",
    "--short",
    is_flag=True,
    default=False,
    help="List packages only.",
)
@click.option(
    "--include-injected",
    is_flag=True,
    default=False,
    help="Show packages injected into the main app's environment.",
)
@options_logging
def run_list(short: bool, include_injected: bool, **_):
    core.list_all_packages(short=short, include_injected=include_injected)
