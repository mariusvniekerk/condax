import sys
import textwrap

import click

from . import config, core, paths


@click.group(
    help=textwrap.dedent(f"""Install and execute applications packaged by conda.

    Conda environment location is {config.CONDA_ENV_PREFIX_PATH}\n
    Links to apps are placed in {config.CONDAX_LINK_DESTINATION}
    """)
)
def cli():
    pass


@cli.command(
    help="""
    Install a package with condax.

    This will install a package into a new conda environment and link the executable
    provided by it to `{config.CONDAX_LINK_DESTINATION}`.
    """
)
@click.option(
    "--channel",
    "-c",
    multiple=True,
    help=f"""Use the channels specified to install.  If not specified condax will
    default to using {config.DEFAULT_CHANNELS}.""",
)
@click.argument("package")
def install(channel, package):
    if channel is None or (len(channel) == 0):
        channel = config.DEFAULT_CHANNELS
    core.install_package(package, channels=channel)


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
@click.option(
    "--channel",
    "-c",
    multiple=True,
    help=f"""Use the channels specified to install.  If not specified condax will
    default to using {config.DEFAULT_CHANNELS}.""",
)
@click.option(
    "--name",
    "-n",
    required=True,
    type=str,
    help=f"""Specify existing environment to inject into.""",
)
@click.argument("package")
def inject(package, name, channel):
    if channel is None or (len(channel) == 0):
        channel = config.DEFAULT_CHANNELS
    core.inject_package_to_env(name, package, channels=channel)


@cli.command(
    help="""
    Uninject a package from existing environment managed by condax.
    """
)
@click.option(
    "--name",
    "-n",
    required=True,
    type=str,
    help=f"""Specify existing environment from which uninject a package""",
)
@click.argument("package")
def unject(package, name):
    core.uninject_package_from_env(name, package)


@cli.command(
    help="""
    Ensure the condax links directory is on $PATH.

    This can update shell configuration files like `~/.bashrc`."""
)
def ensure_path():
    paths.add_path_to_environment(config.CONDAX_LINK_DESTINATION)


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
