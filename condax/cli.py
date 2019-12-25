import click

import userpath

from . import config, paths


@click.group()
def cli():
    pass


@cli.command()
@click.argument("package")
def install(package):
    core.install_package(package)


@cli.command()
@click.argument("package")
def remove(package):
    core.remove_package(package)


@cli.command()
def ensure_path():
    paths.add_path_to_environment(config.CONDAX_LINK_DESTINATION)


if __name__ == "__main__":
    cli()
