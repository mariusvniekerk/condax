import os
import subprocess
import sys

from . import conda
from .config import CONDA_ENV_PREFIX_PATH, CONDAX_LINK_DESTINATION
from .paths import mkpath


def create_links(executables_to_link):
    for exe in executables_to_link:
        executable_name = os.path.basename(exe)
        os.symlink(exe, f"{CONDAX_LINK_DESTINATION}/{executable_name}")


def remove_links(executables_to_unlink):
    for exe in executables_to_unlink:
        executable_name = os.path.basename(exe)
        link_name = f"{CONDAX_LINK_DESTINATION}/{executable_name}"
        if os.path.islink(link_name) and (os.readlink(link_name) == exe):
            os.unlink(link_name)


def install_package(package):
    conda.create_conda_environment(package)
    executables_to_link = conda.detemine_executables_from_env(package)
    mkpath(CONDAX_LINK_DESTINATION)
    create_links(executables_to_link)
    print(f"`{package}` has been installed by condax", file=sys.stderr)


def exit_if_not_installed(package):
    prefix = conda.conda_env_prefix(package)
    if not os.path.exists(prefix):
        print(f"`{package}` is not installed with condax", file=sys.stderr)
        sys.exit(0)


def remove_package(package):
    exit_if_not_installed(package)

    executables_to_unlink = conda.detemine_executables_from_env(package)
    remove_links(executables_to_unlink)
    conda.remove_conda_env(package)
    print(f"`{package}` has been removed from condax", file=sys.stderr)


def update_all_packages():
    for package in os.listdir(CONDA_ENV_PREFIX_PATH):
        if os.path.isdir(os.path.join(CONDA_ENV_PREFIX_PATH, package)):
            update_package(package)


def update_package(package):
    exit_if_not_installed(package)
    try:
        executables_already_linked = set(conda.detemine_executables_from_env(package))
        conda.update_conda_env(package)
        executables_linked_in_updated = set(
            conda.detemine_executables_from_env(package)
        )

        to_delete = executables_linked_in_updated - executables_already_linked
        to_create = executables_already_linked - executables_linked_in_updated

        remove_links(to_delete)
        create_links(to_create)
        print(f"{package} update successfully")

    except subprocess.CalledProcessError:
        print(f"`{package}` could not be updated", file=sys.stderr)
        print(f"removing and recreating instead", file=sys.stderr)

        remove_package(package)
        install_package(package)
