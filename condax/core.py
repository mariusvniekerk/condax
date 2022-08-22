import os
import pathlib
import subprocess
import sys
from enum import Enum

from . import conda
from .config import CONDA_ENV_PREFIX_PATH, CONDAX_LINK_DESTINATION, DEFAULT_CHANNELS
from .paths import mkpath


class LinkConflictAction(Enum):
    ERROR = "error"
    OVERWRITE = "overwrite"
    SKIP = "skip"


def create_link_windows(exe, link_conflict_action):
    executable_name = os.path.basename(exe)
    # create a batch file to run our application
    win_path = pathlib.PureWindowsPath(exe)
    name_only, _ = os.path.splitext(executable_name)
    bat_path = f"{CONDAX_LINK_DESTINATION}/{name_only}.bat"
    if os.path.exists(bat_path):
        if link_conflict_action == LinkConflictAction.ERROR:
            print(
                f"Error: link already exists for {executable_name}, use --link-conflict to overwrite or skip",
                file=sys.stderr,
            )
            sys.exit(1)
        elif link_conflict_action == LinkConflictAction.SKIP:
            print(
                f"Skipping link for {executable_name} because it already exists",
                file=sys.stderr,
            )
            return False
        elif link_conflict_action == LinkConflictAction.OVERWRITE:
            print(f"Overwriting existing link {bat_path}", file=sys.stderr)
            os.remove(bat_path)
    with open(bat_path, "w") as fo:
        fo.writelines(
            [
                "@echo off\n",
                "REM Entrypoint created by condax\n",
                f'CALL "{win_path}" %*',
            ]
        )
    return True


def create_link_unix(exe, link_conflict_action):
    executable_name = os.path.basename(exe)
    dst = f"{CONDAX_LINK_DESTINATION}/{executable_name}"
    if link_conflict_action == LinkConflictAction.OVERWRITE and os.path.exists(dst):
        print(f"Overwriting existing link {dst}", file=sys.stderr)
        os.remove(dst)
    try:
        os.symlink(exe, f"{CONDAX_LINK_DESTINATION}/{executable_name}")
        return True
    except FileExistsError:
        if link_conflict_action == LinkConflictAction.ERROR:
            print(
                f"Error: link already exists for {executable_name}, use --link-conflict to overwrite or skip",
                file=sys.stderr,
            )
            sys.exit(1)
        elif link_conflict_action == LinkConflictAction.SKIP:
            print(
                f"Skipping link for {executable_name} because it already exists",
                file=sys.stderr,
            )
            return False


def create_link(exe, link_conflict_action):
    create_link_func = create_link_windows if sys.platform == "nt" else create_link_unix
    return create_link_func(exe, link_conflict_action)


def create_links(executables_to_link, link_conflict_action):
    print(os.listdir(CONDAX_LINK_DESTINATION))
    link_succeeded = {}
    for exe in executables_to_link:
        link_succeeded[exe] = create_link(exe, link_conflict_action)
    if len(executables_to_link):
        print("Created the following entrypoint links:", file=sys.stderr)
        for exe in executables_to_link:
            if link_succeeded[exe]:
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


def install_package(
    package, channels=DEFAULT_CHANNELS, link_conflict_action=LinkConflictAction.ERROR
):
    conda.create_conda_environment(package, channels=channels)
    executables_to_link = conda.detemine_executables_from_env(package)
    mkpath(CONDAX_LINK_DESTINATION)
    create_links(executables_to_link, link_conflict_action)
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


def update_all_packages(link_conflict_action=LinkConflictAction.ERROR):
    for package in os.listdir(CONDA_ENV_PREFIX_PATH):
        if os.path.isdir(os.path.join(CONDA_ENV_PREFIX_PATH, package)):
            update_package(package, link_conflict_action)


def update_package(package, link_conflict_action=LinkConflictAction.ERROR):
    exit_if_not_installed(package)
    try:
        executables_already_linked = set(conda.detemine_executables_from_env(package))
        conda.update_conda_env(package)
        executables_linked_in_updated = set(
            conda.detemine_executables_from_env(package)
        )

        to_create = executables_linked_in_updated - executables_already_linked
        to_delete = executables_already_linked - executables_linked_in_updated

        remove_links(to_delete)
        create_links(to_create, link_conflict_action)
        print(f"{package} update successfully")

    except subprocess.CalledProcessError:
        print(f"`{package}` could not be updated", file=sys.stderr)
        print(f"removing and recreating instead", file=sys.stderr)

        remove_package(package)
        install_package(package)
