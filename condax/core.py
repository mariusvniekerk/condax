import contextlib
import os
import pathlib
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Collection, Dict, Generator, List, Optional

import typer

from . import conda
from .config import CONFIG, is_windows
from .metadata import PrefixMetadata


class LinkConflictAction(str, Enum):
    ERROR = "error"
    OVERWRITE = "overwrite"
    SKIP = "skip"


def link_path(exe: Path) -> Path:
    if is_windows():
        executable_name = exe.name
        name_only, _ = os.path.splitext(executable_name)
        return CONFIG.link_destination / f"{name_only}.bat"
    else:
        executable_name = exe.name
        return CONFIG.link_destination / executable_name


def create_link_windows(
    exe: Path, link_conflict_action: LinkConflictAction
) -> Optional[Path]:
    executable_name = os.path.basename(exe)
    # create a batch file to run our application
    win_path = pathlib.PureWindowsPath(exe)
    bat_path = link_path(exe)
    if bat_path.exists():
        if link_conflict_action == LinkConflictAction.ERROR:
            link_conflict_error_msg(executable_name)
        elif link_conflict_action == LinkConflictAction.SKIP:
            link_conflict_exists_msg(executable_name)
            return None
        elif link_conflict_action == LinkConflictAction.OVERWRITE:
            typer.secho(
                f"Overwriting existing link {bat_path}", err=True, fg=typer.colors.CYAN
            )
            os.remove(bat_path)
    with open(bat_path, "w") as fo:
        fo.writelines(
            [
                "@echo off\n",
                "REM Entrypoint created by condax\n",
                f'CALL "{win_path}" %*',
            ]
        )
    return bat_path


def create_link_unix(
    exe: Path, link_conflict_action: LinkConflictAction
) -> Optional[Path]:
    executable_name = os.path.basename(exe)
    dst = link_path(exe)
    if link_conflict_action == LinkConflictAction.OVERWRITE and os.path.exists(dst):
        typer.secho(f"Overwriting existing link {dst}", err=True, fg=typer.colors.CYAN)
        os.remove(dst)
    try:
        dest = CONFIG.link_destination / executable_name
        os.symlink(exe, dest)
        return dest
    except FileExistsError:
        if link_conflict_action == LinkConflictAction.ERROR:
            link_conflict_error_msg(executable_name)
        elif link_conflict_action == LinkConflictAction.SKIP:
            link_conflict_exists_msg(executable_name)
    return None


def link_conflict_exists_msg(executable_name: str):
    typer.secho(
        f"Skipping link for {executable_name} because it already exists",
        err=True,
        fg=typer.colors.YELLOW,
    )


def link_conflict_error_msg(executable_name: str):
    typer.secho(
        f"Error: link already exists for {executable_name}, use --link-conflict to overwrite or skip",
        err=True,
        fg=typer.colors.RED,
    )
    sys.exit(1)


def create_link(exe: Path, link_conflict_action: LinkConflictAction) -> Optional[Path]:
    if is_windows():
        return create_link_windows(exe, link_conflict_action)
    else:
        return create_link_unix(exe, link_conflict_action)


def create_links(
    executables_to_link: Collection[Path],
    link_conflict_action: LinkConflictAction,
    env_prefix: Path,
) -> None:
    link_succeeded: Dict[Path, Optional[Path]] = {}
    for exe in executables_to_link:
        link_succeeded[exe] = create_link(exe, link_conflict_action)
    if len(executables_to_link):
        typer.secho(
            "Created the following entrypoint links:", err=True, fg=typer.colors.CYAN
        )
        for exe in executables_to_link:
            if link_succeeded[exe]:
                executable_name = os.path.basename(exe)
                typer.secho(f"    {executable_name}", err=True, fg=typer.colors.CYAN)

    with prefix_metadata(env_prefix) as metadata:
        metadata.links.update(
            {k: v for k, v in link_succeeded.items() if v is not None}
        )


@contextlib.contextmanager
def prefix_metadata(env_prefix: Path) -> Generator[PrefixMetadata, None, None]:
    metadata_path = env_prefix / ".condax-metadata.json"
    if metadata_path.exists():
        ret = PrefixMetadata.parse_file(metadata_path)
    else:
        ret = PrefixMetadata(prefix=env_prefix)
    yield ret

    def encoder(obj: Any) -> "str | Any":
        if isinstance(obj, Path):
            return str(obj)
        return obj

    metadata_path.write_text(ret.json(indent=2, exclude_unset=True, encoder=encoder))


def remove_links(executables_to_unlink: Collection[Path], env_prefix: Path) -> None:
    removed_links: Dict[Path, Path] = {}

    for exe in executables_to_unlink:
        link = link_path(exe)
        if is_windows():
            os.unlink(link)
            removed_links[exe] = link
        else:
            if os.path.islink(link) and (os.readlink(link) == exe):
                os.unlink(link)
                removed_links[exe] = link

    if len(executables_to_unlink):
        typer.secho(
            "Removed the following entrypoint links:", err=True, fg=typer.colors.CYAN
        )
        for exe in executables_to_unlink:
            executable_name = os.path.basename(exe)
            typer.secho(f"    {executable_name}", err=True, fg=typer.colors.CYAN)

    with prefix_metadata(env_prefix) as metadata:
        for k in removed_links:
            if k in metadata.links:
                del metadata.links[k]


def install_package(
    package: str,
    channels: Optional[List[str]] = None,
    link_conflict_action=LinkConflictAction.ERROR,
) -> None:
    if channels is None:
        channels = CONFIG.channels
    conda.create_conda_environment(package, channels=channels)
    executables_to_link = conda.detemine_executables_from_env(package)
    CONFIG.link_destination.mkdir(parents=True, exist_ok=True)
    create_links(
        executables_to_link,
        link_conflict_action,
        env_prefix=conda.conda_env_prefix(package),
    )
    typer.secho(
        f"`{package}` has been installed by condax", err=True, fg=typer.colors.GREEN
    )


def inject_packages(
    package: str,
    extra_packages: List[str],
    channels: Optional[List[str]] = None,
    include_apps: bool = False,
    link_conflict_action=LinkConflictAction.ERROR,
) -> None:
    if channels is None:
        channels = CONFIG.channels

    prefix = conda.conda_env_prefix(package)
    conda.install_conda_packages(extra_packages, channels=channels, prefix=prefix)
    if include_apps:
        for extra_package in extra_packages:
            executables_to_link = conda.detemine_executables_from_env(
                extra_package, env_prefix=prefix
            )
            CONFIG.link_destination.mkdir(parents=True, exist_ok=True)
            create_links(executables_to_link, link_conflict_action, env_prefix=prefix)
    with prefix_metadata(prefix) as metadata:
        metadata.injected_packages = list(
            sorted(set(metadata.injected_packages) | set(extra_packages))
        )
        if include_apps:
            metadata.injected_packages_with_apps = list(
                sorted(set(metadata.injected_packages_with_apps) | set(extra_packages))
            )

    typer.secho(
        f"`{' '.join(extra_packages)}` have been installed into {prefix} by condax",
        err=True,
        fg=typer.colors.GREEN,
    )


def exit_if_not_installed(package: str):
    prefix = conda.conda_env_prefix(package)
    if not os.path.exists(prefix):
        typer.secho(
            f"`{package}` is not installed with condax", err=True, fg=typer.colors.RED
        )
        sys.exit(0)


def remove_package(package) -> None:
    exit_if_not_installed(package)
    executables_to_unlink = conda.detemine_executables_from_env(package)
    prefix = conda.conda_env_prefix(package)
    remove_links(executables_to_unlink, env_prefix=prefix)
    with prefix_metadata(prefix) as metadata:
        additional_removals = metadata.links.keys()
    remove_links(additional_removals, env_prefix=prefix)

    conda.remove_conda_env(package)
    typer.secho(
        f"`{package}` has been removed from condax", err=True, fg=typer.colors.GREEN
    )


def update_all_packages(link_conflict_action=LinkConflictAction.ERROR) -> None:
    for package in CONFIG.prefix_path.iterdir():
        if package.is_dir():
            update_package(package.name, link_conflict_action)


def prefix(package: str) -> Path:
    exit_if_not_installed(package)
    return conda.conda_env_prefix(package)


def update_package(package: str, link_conflict_action=LinkConflictAction.ERROR) -> None:
    exit_if_not_installed(package)
    env_prefix = conda.conda_env_prefix(package)
    with prefix_metadata(env_prefix) as metadata:
        executables_already_linked = set(metadata.links.keys())
        injected = metadata.injected_packages
        injected_with_apps = metadata.injected_packages_with_apps
    try:
        executables_already_linked |= set(conda.detemine_executables_from_env(package))

        conda.update_conda_env(package)
        env_prefix = conda.conda_env_prefix(package)
        executables_linked_in_updated = set(
            conda.detemine_executables_from_env(package)
        )
        for p in injected_with_apps:
            executables_linked_in_updated |= set(
                conda.detemine_executables_from_env(p, env_prefix=env_prefix)
            )

        to_create = executables_linked_in_updated - executables_already_linked
        to_delete = executables_already_linked - executables_linked_in_updated

        remove_links(to_delete, env_prefix=env_prefix)
        create_links(to_create, link_conflict_action, env_prefix=env_prefix)
        typer.secho(f"`{package}` has been updated", err=True, fg=typer.colors.GREEN)

    except subprocess.CalledProcessError:
        typer.secho(
            f"`{package}` could not be updated", err=True, fg=typer.colors.YELLOW
        )
        typer.secho(
            f"removing and recreating instead", err=True, fg=typer.colors.YELLOW
        )

        remove_package(package)
        install_package(package)
        if injected:
            inject_packages(package, injected, include_apps=False)
        if injected_with_apps:
            inject_packages(package, injected_with_apps, include_apps=True)
        typer.secho(f"`{package}` has been updated", err=True, fg=typer.colors.GREEN)
