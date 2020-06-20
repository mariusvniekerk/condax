import os
import pathlib
import subprocess
import sys
import tempfile

from . import conda
from .config import CONDA_ENV_PREFIX_PATH, CONDAX_LINK_DESTINATION, DEFAULT_CHANNELS
from .paths import mkpath


def symlink(target, link_name, overwrite=False):
    """
    https://stackoverflow.com/questions/8299386/

    Create a symbolic link named link_name pointing to target.
    If link_name exists then FileExistsError is raised, unless overwrite=True.
    When trying to overwrite a directory, IsADirectoryError is raised.
    """
    if not overwrite:
        os.symlink(target, link_name)
        return

    # os.replace() may fail if files are on different filesystems
    link_dir = os.path.dirname(link_name)

    # Create link to target with temporary filename
    while True:
        temp_link_name = tempfile.mktemp(dir=link_dir)

        # os.* functions mimic as closely as possible system functions
        # The POSIX symlink() returns EEXIST if link_name already exists
        # https://pubs.opengroup.org/onlinepubs/9699919799/functions/symlink.html
        try:
            os.symlink(target, temp_link_name)
            break
        except FileExistsError:
            pass

    # Replace link_name with temp_link_name
    try:
        # Pre-empt os.replace on a directory with a nicer message
        if os.path.isdir(link_name):
            raise IsADirectoryError(f"Cannot symlink over existing directory: '{link_name}'")
        os.replace(temp_link_name, link_name)
    except:
        if os.path.islink(temp_link_name):
            os.remove(temp_link_name)
        raise


def create_link(exe):
    executable_name = os.path.basename(exe)
    if os.name == "nt":
        # create a batch file to run our application
        win_path = pathlib.PureWindowsPath(exe)
        name_only, _ = os.path.splitext(executable_name)
        with open(f"{CONDAX_LINK_DESTINATION}/{name_only}.bat", "w") as fo:
            fo.writelines(["REM Entrypoint created by condax", f'CALL "{win_path}" %*'])
    else:
        symlink(exe, f"{CONDAX_LINK_DESTINATION}/{executable_name}", overwrite=True)


def create_links(executables_to_link):
    for exe in executables_to_link:
        create_link(exe)
    if len(executables_to_link):
        print("Created the following entrypoint links:", file=sys.stderr)
        for exe in executables_to_link:
            executable_name = os.path.basename(exe)
            print(f"    {executable_name}", file=sys.stderr)


def remove_links(executables_to_unlink):
    for exe in executables_to_unlink:
        executable_name = os.path.basename(exe)
        link_name = f"{CONDAX_LINK_DESTINATION}/{executable_name}"
        if os.path.islink(link_name) and (os.readlink(link_name) == exe):
            os.unlink(link_name)
    if len(executables_to_unlink):
        print("Removed the following entrypoint links:", file=sys.stderr)
        for exe in executables_to_unlink:
            executable_name = os.path.basename(exe)
            print(f"    {executable_name}", file=sys.stderr)


def install_package(package, channels=DEFAULT_CHANNELS):
    conda.create_conda_environment(package, channels=channels)
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
