import sys
from typing import List, Optional

import typer

from . import __version__, config, core, paths

cli = typer.Typer(
    name="condax",
    help="Install and execute applications packaged by conda.",
    no_args_is_help=True,
)

_OPTION_MAMBA = typer.Option(
    False,
    "--mamba",
    help="Force using mamba.",
)
_OPTION_LINK_ACTION = typer.Option(
    core.LinkConflictAction.ERROR,
    "--link-conflict",
    "-l",
    help=f"""\
            How to handle conflicts when a link with the same name already exists in
            `{config.CONFIG.link_destination}`.  If `error` is specified, condax will exit with
            an error if the link already exists.  If `overwrite` is specified, condax will
            overwrite the existing link.  If `skip` is specified, condax will skip linking the
            conflicting executable.""",
)


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit(0)


@cli.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print version and exit",
    ),
):
    return


@cli.command(
    help=f"""\
        Install a package with condax.

        This will install a package into a new conda environment and link the executable
        provided by it to `{config.CONFIG.link_destination}`.
        """,
)
def install(
    channel: Optional[List[str]] = typer.Option(
        None,
        "--channel",
        "-c",
        help=f"""\
            Use the channels specified to install.  If not specified condax will
            default to using {config.CONFIG.channels}.""",
    ),
    link_conflict: core.LinkConflictAction = _OPTION_LINK_ACTION,
    mamba: bool = _OPTION_MAMBA,
    package: str = typer.Argument(...),
):
    if channel is None or (len(channel) == 0):
        channel = config.CONFIG.channels
    config.CONFIG.ensure_conda_executable(require_mamba=mamba)

    core.install_package(
        package,
        channels=channel,
        link_conflict_action=link_conflict,
    )


@cli.command(
    help=f"""\
        Inject a package into a condax managed environment.

        This will install a package into an existing condax environment.
        """,
)
def inject(
    channel: Optional[List[str]] = typer.Option(
        None,
        "--channel",
        "-c",
        help=f"""\
            Use the channels specified to install.  If not specified condax will
            default to using {config.CONFIG.channels}.""",
    ),
    mamba: bool = _OPTION_MAMBA,
    link_conflict: core.LinkConflictAction = _OPTION_LINK_ACTION,
    include_apps: bool = typer.Option(
        False, "--include-apps", help="Adds applications of injected package to PATH."
    ),
    package: str = typer.Argument(..., help="The condax environment inject into."),
    extra_packages: List[str] = typer.Argument(..., help="Extra packages to install."),
):
    if channel is None or (len(channel) == 0):
        channel = config.CONFIG.channels
    config.CONFIG.ensure_conda_executable(require_mamba=mamba)

    core.inject_packages(
        package,
        extra_packages,
        channels=channel,
        link_conflict_action=link_conflict,
        include_apps=include_apps,
    )


@cli.command(
    help="""
    Remove a package installed by condax.

    This will remove a package installed with condax and destroy the underlying
    conda environment.
    """
)
def remove(
    package: str,
    mamba: bool = _OPTION_MAMBA,
):
    config.CONFIG.ensure_conda_executable(require_mamba=mamba)

    core.remove_package(package)


@cli.command(
    help="""
    Ensure the condax links directory is on $PATH.

    This can update shell configuration files like `~/.bashrc`."""
)
def ensure_path() -> None:
    paths.add_path_to_environment(config.CONFIG.link_destination)


@cli.command(help="""Display the conda prefix for a condax package.""")
def prefix(package: str) -> None:
    typer.echo(core.prefix(package))


@cli.command(
    help="""
    Update package(s) installed by condax.

    This will update the underlying conda environments(s) to the latest release of a package.
"""
)
def update(
    all: bool = typer.Option(
        False, "--all", help="Set to update all packages installed by condax"
    ),
    link_conflict: core.LinkConflictAction = _OPTION_LINK_ACTION,
    mamba: bool = _OPTION_MAMBA,
    package: Optional[str] = typer.Argument(None),
):
    config.CONFIG.ensure_conda_executable(require_mamba=mamba)
    if all and package is not None:
        typer.echo("Cannot specify --all and a package name")
        sys.exit(1)
    if all:
        core.update_all_packages(link_conflict)
    elif package:
        core.update_package(package, link_conflict)
    else:
        typer.echo("Must specify --all or a package name")
        sys.exit(1)


if __name__ == "__main__":
    cli()
