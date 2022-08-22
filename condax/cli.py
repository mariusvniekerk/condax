import sys

import click

from . import config, core, paths


@click.group(help="Install and execute applications packaged by conda.")
def cli():
    pass


@cli.command(
    help=f"""
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
@click.option(
    "--link-conflict",
    "-l",
    default="error",
    type=click.Choice([action.value for action in core.LinkConflictAction]),
    help=f"""How to handle conflicts when a link with the same name already exists in
    `{config.CONDAX_LINK_DESTINATION}`.  If `error` is specified, condax will exit with
    an error if the link already exists.  If `overwrite` is specified, condax will
    overwrite the existing link.  If `skip` is specified, condax will skip linking the
    conflicting executable.""",
)
@click.argument("package")
def install(channel, package, link_conflict):
    if channel is None or (len(channel) == 0):
        channel = config.DEFAULT_CHANNELS
    core.install_package(
        package,
        channels=channel,
        link_conflict_action=core.LinkConflictAction(link_conflict),
    )


@cli.command(
    help="""
    Remove a package installed by condax.

    This will remove a package installed with condax and destroy the underlying
    conda environment.
    """
)
@click.argument("package")
def remove(package):
    core.remove_package(package)


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
@click.option(
    "--link-conflict",
    "-l",
    default="error",
    type=click.Choice([action.value for action in core.LinkConflictAction]),
    help=f"""How to handle conflicts when a link with the same name already exists in
    `{config.CONDAX_LINK_DESTINATION}`.  If `error` is specified, condax will exit with
    an error if the link already exists.  If `overwrite` is specified, condax will
    overwrite the existing link.  If `skip` is specified, condax will skip linking the
    conflicting executable.""",
)
@click.argument("package", default="", required=False)
@click.pass_context
def update(ctx, all, link_conflict, package):
    if all:
        core.update_all_packages(core.LinkConflictAction(link_conflict))
    elif package:
        core.update_package(package, core.LinkConflictAction(link_conflict))
    else:
        print(ctx.get_help(), file=sys.stderr)


if __name__ == "__main__":
    cli()
