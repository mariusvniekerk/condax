from pathlib import Path
import sys
from typing import List, Optional

import click

import condax.config as config
import condax.conda as conda
import condax.core as core
import condax.paths as paths
import condax.migrate as migrate
from condax import __version__


option_config = click.option(
    "--config",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    help=f"Custom path to a condax config file in YAML. Default: {config.DEFAULT_CONFIG}",
)

option_channels = click.option(
    "--channel",
    "-c",
    "channels",
    multiple=True,
    help=f"""Use the channels specified to install. If not specified condax will
    default to using {config.DEFAULT_CHANNELS}, or 'channels' in the config file.""",
)

option_envname = click.option(
    "--name",
    "-n",
    "envname",
    required=True,
    prompt="Specify the environment (Run `condax list --short` to see available ones)",
    type=str,
    help=f"""Specify existing environment to inject into.""",
    callback=lambda ctx, param, value: value.strip(),
)

option_is_forcing = click.option(
    "-f",
    "--force",
    "is_forcing",
    help="""Modify existing environment and files in CONDAX_BIN_DIR.""",
    is_flag=True,
    default=False,
)


@click.group(
    help=f"""Install and execute applications packaged by conda.

    Default varibles:

      Conda environment location is {config.DEFAULT_PREFIX_DIR}\n
      Links to apps are placed in {config.DEFAULT_BIN_DIR}
    """
)
@click.version_option(
    __version__,
    message="%(prog)s %(version)s",
)
@option_config
def cli(config_file: Optional[Path]):
    if config_file:
        config.set_via_file(config_file)
    else:
        config.set_via_file(config.DEFAULT_CONFIG)


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
@click.argument("packages", nargs=-1)
def install(
    packages: List[str],
    config_file: Optional[Path],
    channels: List[str],
    is_forcing: bool,
):
    if config_file:
        config.set_via_file(config_file)
    if channels:
        config.set_via_value(channels=channels)
    for pkg in packages:
        core.install_package(pkg, is_forcing=is_forcing)


@cli.command(
    help="""
    Remove a package.

    This will remove a package installed with condax and destroy the underlying
    conda environment.
    """
)
@click.argument("packages", nargs=-1)
def remove(packages: List[str]):
    for pkg in packages:
        core.remove_package(pkg)


@cli.command(
    help="""
    Alias for condax remove.
    """
)
@click.argument("packages", nargs=-1)
def uninstall(packages: List[str]):
    remove(packages)


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
@click.option(
    "--include-injected",
    is_flag=True,
    default=False,
    help="Show packages injected into the main app's environment.",
)
def list(short: bool, include_injected: bool):
    core.list_all_packages(short=short, include_injected=include_injected)


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
@click.argument("packages", nargs=-1, required=True)
def inject(
    packages: List[str],
    envname: str,
    channels: List[str],
    is_forcing: bool,
    include_apps: bool,
):
    if channels:
        config.set_via_value(channels=channels)

    core.inject_package_to(
        envname, packages, is_forcing=is_forcing, include_apps=include_apps
    )


@cli.command(
    help="""
    Uninject a package from an existing environment.
    """
)
@option_envname
@click.argument("packages", nargs=-1, required=True)
def uninject(packages: List[str], envname: str):
    core.uninject_package_from(envname, packages)


@cli.command(
    help="""
    Ensure the condax links directory is on $PATH.
    """
)
@option_config
def ensure_path(config_file: Optional[Path]):
    if config_file:
        config.set_via_file(config_file)
    paths.add_path_to_environment(config.C.bin_dir())


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
@click.argument("packages", required=False, nargs=-1)
@click.pass_context
def update(ctx: click.Context, all: bool, packages: List[str], update_specs: bool):
    if all:
        core.update_all_packages(update_specs)
    elif packages:
        for pkg in packages:
            core.update_package(pkg, update_specs)
    else:
        print(ctx.get_help(), file=sys.stderr)


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
def export(dir: str):
    core.export_all_environments(dir)


@cli.command(
    "import",
    help="""
    [experimental] Import condax environments.
    """,
)
@option_is_forcing
@click.argument(
    "directory",
    required=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
def run_import(directory: str, is_forcing: bool):
    core.import_environments(directory, is_forcing)


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
def repair(is_migrating):
    if is_migrating:
        migrate.from_old_version()
    conda.setup_micromamba()
    core.fix_links()


if __name__ == "__main__":
    cli()
