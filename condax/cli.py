import click

from . import core


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


if __name__ == "__main__":
    cli()
