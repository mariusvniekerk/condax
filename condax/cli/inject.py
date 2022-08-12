import logging
from typing import List
import click

import condax.config as config
import condax.core as core
from condax import __version__

from . import cli, option_channels, option_envname, option_is_forcing, options_logging


@cli.command(
    help="""
    Inject a package to existing environment created by condax.
    """
)
@option_channels
@option_envname
@option_is_forcing
@click.option(
    "--include-apps",
    help="""Make apps from the injected package available.""",
    is_flag=True,
    default=False,
)
@options_logging
@click.argument("packages", nargs=-1, required=True)
def inject(
    packages: List[str],
    envname: str,
    is_forcing: bool,
    include_apps: bool,
    verbose: int,
    **_,
):
    core.inject_package_to(
        envname,
        packages,
        is_forcing=is_forcing,
        include_apps=include_apps,
        conda_stdout=verbose <= logging.INFO,
    )


@cli.command(
    help="""
    Uninject a package from an existing environment.
    """
)
@option_envname
@options_logging
@click.argument("packages", nargs=-1, required=True)
def uninject(packages: List[str], envname: str, verbose: int, **_):
    core.uninject_package_from(envname, packages, verbose <= logging.INFO)
