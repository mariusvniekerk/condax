import collections
import logging
import os
import pathlib
import shlex
import subprocess
import shutil
import sys
from typing import Iterable, List

from . import conda
from condax.config import C
from .paths import mkpath
from . import wrapper
import condax.utils as utils


Path = pathlib.Path


def create_link(package: str, exe: Path, is_forcing: bool = False):
    executable_name = exe.name
    # TODO: enable `mamba run` option after hiding the banner
    conda_exe = conda.ensure_conda(mamba_ok=False)
    prefix = conda.conda_env_prefix(package)
    if os.name == "nt":
        # create a batch file to run our application
        win_path = pathlib.PureWindowsPath(exe)
        name_only, _ = os.path.splitext(executable_name)
        script_path = C.bin_dir() / f"{name_only}.bat"
        if script_path.exists():
            print(f"[warning] {name_only}.bat already exists; overwriting it...")
        with open(script_path, "w") as fo:
            fo.writelines(
                [
                    "@echo off\n",
                    "REM Entrypoint created by condax\n",
                    f"{conda_exe} run --prefix {prefix} {executable_name} %*\n",
                ]
            )
    else:
        script_path = C.bin_dir() / executable_name
        if script_path.exists() and not is_forcing:
            user_input = input(f"{executable_name} already exists. Overwrite? (y/N) ")
            if user_input.strip().lower() not in ("y", "yes"):
                print(f"Skip installing app: {executable_name}...")
                return

        with open(script_path, "w") as fo:
            fo.writelines(
                [
                    "#!/usr/bin/env bash\n",
                    "\n",
                    "# Entrypoint created by condax\n",
                    f"{conda_exe} run --prefix {prefix} {executable_name} $@\n",
                ]
            )
        shutil.copystat(exe, script_path)


def create_links(package: str, executables_to_link: Iterable[Path], is_forcing: bool=False):
    if executables_to_link:
        print("Created the following entrypoint links:", file=sys.stderr)

    for exe in sorted(executables_to_link):
        executable_name = exe.name
        print(f"    {executable_name}", file=sys.stderr)
        create_link(package, exe, is_forcing)


def remove_links(package: str, executables_to_unlink: Iterable[Path]):
    if executables_to_unlink:
        print("Removed the following entrypoint links:", file=sys.stderr)

    for exe in executables_to_unlink:
        executable_name = exe.name
        link_path = C.bin_dir() / executable_name
        wrapper_env = wrapper.read_env_name(link_path)
        if wrapper_env is None:
            print(f"    {executable_name} \t (failed to get env)")
            link_path.unlink()
        elif wrapper_env == package:
            print(f"    {executable_name}", file=sys.stderr)
            link_path.unlink()
        else:
            logging.info(
                f"Keep {executable_name} as it runs in {wrapper_env}, not {package}."
            )


def install_package(package: str, channels: List[str] = C.channels(), is_forcing: bool=False):
    # package match specifications
    # https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications
    package, match_specs = utils.split_match_specs(package)

    if conda.has_conda_env(package):
        if is_forcing:
            conda.remove_conda_env(package)
        else:
            print(
                f"`{package}` is already installed. Run `condax update {package}` to update.",
                file=sys.stderr,
            )
            sys.exit(1)

    conda.create_conda_environment(package, channels=channels, match_specs=match_specs)
    executables_to_link = conda.determine_executables_from_env(package)
    mkpath(C.bin_dir())
    create_links(package, executables_to_link, is_forcing=is_forcing)
    print(f"`{package}` has been installed by condax", file=sys.stderr)


def inject_package_to_env(
    env_name: str,
    injected_package: str,
    channels: List[str] = C.channels(),
    match_specs: str = "",
    is_forcing: bool = False,
):
    if not conda.has_conda_env(env_name):
        print(
            f"`{env_name}` does not exist; Abort injecting `{injected_package}`...",
            file=sys.stderr,
        )
        sys.exit(1)

    # package match specifications
    # https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications
    injected_package, match_specs = utils.split_match_specs(injected_package)
    conda.inject_to_conda_env(
        injected_package, env_name, channels=channels, match_specs=match_specs,
    )
    # TODO: add scripts only if --include-apps
    if False:
        executables_to_link = conda.determine_executables_from_env(
            env_name, injected_package,
        )
        create_links(env_name, executables_to_link, is_forcing=is_forcing)
    print(f"`{injected_package}` has been injected to `{env_name}`", file=sys.stderr)


def uninject_package_from_env(env_name, injected_package):
    if not conda.has_conda_env(env_name):
        print(
            f"`{env_name}` does not exist; Abort uninjecting `{injected_package}`...",
            file=sys.stderr,
        )
        sys.exit(1)

    conda.uninject_from_conda_env(injected_package, env_name)
    # TODO: remove scripts only if injected with --include-apps option
    if False:
        executables_to_link = conda.determine_executables_from_env(
            env_name, injected_package
        )
        remove_links(env_name, executables_to_link)
    print(
        f"`{injected_package}` has been uninjected from `{env_name}`", file=sys.stderr
    )


def exit_if_not_installed(package: str):
    prefix = conda.conda_env_prefix(package)
    if not prefix.exists():
        print(f"`{package}` is not installed with condax", file=sys.stderr)
        sys.exit(0)


def remove_package(package):
    exit_if_not_installed(package)

    executables_to_unlink = conda.determine_executables_from_env(package)
    remove_links(package, executables_to_unlink)
    conda.remove_conda_env(package)
    print(f"`{package}` has been removed from condax", file=sys.stderr)


def update_all_packages(is_forcing: bool=False):
    for package_dir in C.prefix_dir().iterdir():
        package = package_dir.name
        update_package(package, is_forcing=is_forcing)


def list_all_packages(short=False):
    packages = [pkg_dir.name for pkg_dir in C.prefix_dir().iterdir()]
    packages.sort()
    executable_counts = collections.Counter()

    # messages follow pipx's text format
    if not short:
        print(f"conda envs are in {C.prefix_dir()}")
        print(f"apps are exposed on your $PATH at {C.bin_dir()}")

    for package in packages:
        _, python_version, _ = conda.get_package_info(package, "python")
        package_name, package_version, package_build = conda.get_package_info(package)

        if short:
            package_header = f"{package_name} {package_version}"
            print(package_header)

        else:
            package_header = "".join(
                [
                    f"  package {shlex.quote(package_name)}",
                    f" {package_version} ({package_build})",
                    f", using Python {python_version}" if python_version else "",
                ]
            )
            print(package_header)

            try:
                paths = conda.determine_executables_from_env(package)
                names = [path.name for path in paths]
                executable_counts.update(names)
                for name in sorted(names):
                    print(f"    - {name}")

            except ValueError:
                print("    (no executables found)")

    # warn if duplicate executables are found
    duplicates = [name for (name, cnt) in executable_counts.items() if cnt > 1]
    if duplicates:
        print(f"\n[warning] The following executables are duplicated:")
        for name in duplicates:
            print(f"    * {name}")
        print()


def update_package(package: str, is_forcing: bool=False):
    exit_if_not_installed(package)
    try:
        executables_already_linked = set(conda.determine_executables_from_env(package))
        conda.update_conda_env(package)
        executables_linked_in_updated = set(
            conda.determine_executables_from_env(package)
        )

        to_create = executables_linked_in_updated - executables_already_linked
        to_delete = executables_already_linked - executables_linked_in_updated

        create_links(package, to_create, is_forcing)
        remove_links(package, to_delete)
        print(f"{package} update successfully")

    except subprocess.CalledProcessError:
        print(f"`{package}` could not be updated", file=sys.stderr)
        print(f"removing and recreating instead", file=sys.stderr)

        remove_package(package)
        install_package(package, is_forcing=is_forcing)
