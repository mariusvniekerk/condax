import pathlib
import sys
import textwrap

import click

from . import config, core, paths


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

      Conda environment location is {config.CONDAX_ENV_PREFIX_DIR}\n
      Links to apps are placed in {config.CONDAX_LINK_DESTINATION}
    """
    ),
)
@click.option(
    "--config",
    "config_file",
    type=pathlib.Path,
    default=pathlib.Path(config.CONDAX_CONFIG_PATH),
    help="Path to a YAML file containing configuration options.",
)
@click.pass_context
def cli(ctx, config_file):
    ctx.ensure_object(dict)  # don't forget this!
    ctx.config = config.set_defaults_if_absent(config_file)


@cli.command(
    help="""
    Install a package with condax.

    This will install a package into a new conda environment and link the executable
    provided by it to `{config.CONDAX_LINK_DESTINATION}`.
    """
)
@option_channels
@click.pass_context
@click.argument("package")
def install(ctx, channels, package):
    channels = channels if channels else ctx.config["channels"]
    core.install_package(package, channels=channels)


@cli.command(
    help="""
    Remove a package.

    This will remove a package installed with condax and destroy the underlying
    conda environment.
    """
)
@click.pass_context
@click.argument("package")
def remove(ctx, package):
    core.remove_package(package)


@cli.command(
    help="""
    Alias for conda remove.
    """
)
@click.pass_context
@click.argument("package")
def uninstall(ctx, package):
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
@click.pass_context
def list(ctx, short):
    print(f'{ctx.config = }')
    core.list_all_packages(short)


@cli.command(
    help="""
    Inject a package to existing environment created by condax.
    """
)
@option_channels
@option_envname
@click.pass_context
@click.argument("package")
def inject(ctx, package, envname, channels):
    channels = channels if channels else ctx.config['channels']
    core.inject_package_to_env(envname, package, channels=channels)


@cli.command(
    help="""
    Uninject a package from existing environment managed by condax.
    """
)
@option_envname
@click.pass_context
@click.argument("package")
def unject(ctx, package, envname):
    core.uninject_package_from_env(envname, package)


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
    cli(config={})
