import pathlib
import sys
import textwrap

import click

from . import config, core, paths
from condax.config import C

option_channels = click.option(
    "--channel",
    "-c",
    "channels",
    multiple=True,
    help=f"""Use the channels specified to install.  If not specified condax will
    default to using {config.DEFAULT_CHANNELS}.""",
)

option_envname = click.option(
    "--name",
    "-n",
    "envname",
    required=True,
    prompt=True,
    type=str,
    help=f"""Specify existing environment to inject into.""",
)


@click.group(
    chain=True,
    help=textwrap.dedent(
        f"""Install and execute applications packaged by conda.

    Default varibles:

      Conda environment location is {config.DEFAULT_PREFIX_DIR}\n
      Links to apps are placed in {config.DEFAULT_BIN_DIR}
    """
    ),
)
@click.option(
    "--config",
    "config_file",
    type=pathlib.Path,
    default=pathlib.Path(config.DEFAULT_CONFIG),
    help="Path to a YAML file containing configuration options.",
)
def cli(config_file):
    config.set_via_file(config_file)


@cli.command(
    help=f"""
    Install a package with condax.

    This will install a package into a new conda environment and link the executable
    provided by it to `{config.DEFAULT_BIN_DIR}`.
    """
)
@option_channels
@click.argument("package")
def install(package, channels):
    channels = channels if channels else C.channels()
    core.install_package(package, channels)


@cli.command(
    help="""
    Remove a package.

    This will remove a package installed with condax and destroy the underlying
    conda environment.
    """
)
@click.argument("package")
def remove(package):
    core.remove_package(package)


@cli.command(
    help="""
    Alias for conda remove.
    """
)
@click.argument("package")
def uninstall(package):
    core.remove_package(package)


@cli.command(
    help="""
    List packages managed by condax.

    This will show all packages installed by condax.
    """
)
@click.option(
    "--short",
    is_flag=True,
    default=False,
    help="List packages only.",
)
def list(short):
    core.list_all_packages(short)


@cli.command(
    help="""
    Inject a package to existing environment created by condax.
    """
)
@option_channels
@option_envname
@click.argument("package")
def inject(package, envname, channels):
    channels = channels if channels else C.channels()
    core.inject_package_to_env(envname, package, channels=channels)


@cli.command(
    help="""
    Uninject a package from existing environment managed by condax.
    """
)
@option_envname
@click.argument("package")
def unject(package, envname):
    core.uninject_package_from_env(envname, package)


@cli.command(
    help="""
    Ensure the condax links directory is on $PATH.

    This can update shell configuration files like `~/.bashrc`."""
)
def ensure_path():
    paths.add_path_to_environment(config.DEFAULT_BIN_DIR)


@cli.command(
    help="""
    Update package(s) installed by condax.

    This will update the underlying conda environments(s) to the latest release of a package.
"""
)
@click.option(
    "--all", is_flag=True, help="Set to update all packages installed by condax"
)
@click.argument("package", default="", required=False)
@click.pass_context
def update(ctx, all, package):
    if all:
        core.update_all_packages()
    elif package:
        core.update_package(package)
    else:
        print(ctx.get_help(), file=sys.stderr)


if __name__ == "__main__":
    cli()
