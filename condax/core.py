import collections
import logging
import os
import shlex
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List

import condax.conda as conda
import condax.metadata as metadata
import condax.wrapper as wrapper
import condax.utils as utils
from condax.config import C
from condax.paths import mkpath


def create_link(package: str, exe: Path, is_forcing: bool = False):
    executable_name = exe.name
    # TODO: enable `mamba run` option after hiding the banner
    conda_exe = conda.ensure_conda(mamba_ok=False)
    prefix = conda.conda_env_prefix(package)
    if os.name == "nt":
        script_lines = [
            "@echo off\n",
            "REM Entrypoint created by condax\n",
            f"{conda_exe} run --prefix {prefix} {executable_name} %*\n",
        ]
        ext = ".bat"
    else:
        script_lines = [
            "#!/usr/bin/env bash\n",
            "\n",
            "# Entrypoint created by condax\n",
            f'{conda_exe} run --prefix {prefix} {executable_name} "$@"\n',
        ]
        ext = ""

    script_path = C.bin_dir() / (executable_name + ext)
    if script_path.exists() and not is_forcing:
        user_input = input(f"{executable_name} already exists. Overwrite? (y/N) ")
        if user_input.strip().lower() not in ("y", "yes"):
            print(f"Skip installing app: {executable_name}...")
            return
    with open(script_path, "w") as fo:
        fo.writelines(script_lines)
    shutil.copystat(exe, script_path)


def create_links(
    package: str, executables_to_link: Iterable[Path], is_forcing: bool = False
):
    if executables_to_link:
        print("Created the following entrypoint links:", file=sys.stderr)

    for exe in sorted(executables_to_link):
        executable_name = exe.name
        print(f"    {executable_name}", file=sys.stderr)
        create_link(package, exe, is_forcing)


def remove_links(package: str, app_names_to_unlink: Iterable[str]):
    if app_names_to_unlink:
        print("Removed the following entrypoint links:", file=sys.stderr)

    for executable_name in app_names_to_unlink:
        link_path = C.bin_dir() / executable_name
        wrapper_env = wrapper.read_env_name(link_path)
        if wrapper_env is None:
            print(f"    {executable_name} \t (failed to get env)")
            link_path.unlink(missing_ok=True)
        elif wrapper_env == package:
            print(f"    {executable_name}", file=sys.stderr)
            link_path.unlink()
        else:
            logging.info(
                f"Keep {executable_name} as it runs in {wrapper_env}, not {package}."
            )


def install_package(
    package: str,
    is_forcing: bool = False,
):
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

    conda.create_conda_environment(package, match_specs=match_specs)
    executables_to_link = conda.determine_executables_from_env(package)
    mkpath(C.bin_dir())
    create_links(package, executables_to_link, is_forcing=is_forcing)
    _create_metadata(package)
    print(f"`{package}` has been installed by condax", file=sys.stderr)


def inject_package_to(
    env_name: str,
    injected_package: str,
    match_specs: str = "",
    is_forcing: bool = False,
    include_apps: bool = False,
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
        injected_package,
        env_name,
        match_specs=match_specs,
    )

    # update the metadata
    _inject_to_metadata(env_name, injected_package, include_apps)

    # Add links only if --include-apps is set
    if include_apps:
        executables_to_link = conda.determine_executables_from_env(
            env_name,
            injected_package,
        )
        create_links(env_name, executables_to_link, is_forcing=is_forcing)
    print(f"`{injected_package}` has been injected to `{env_name}`", file=sys.stderr)


def uninject_package_from(env_name: str, injected_package: str):
    if not conda.has_conda_env(env_name):
        print(
            f"`{env_name}` does not exist; Abort uninjecting `{injected_package}`...",
            file=sys.stderr,
        )
        sys.exit(1)

    conda.uninject_from_conda_env(injected_package, env_name)

    injected_app_names = _get_injected_apps(env_name, injected_package)
    remove_links(env_name, injected_app_names)
    _uninject_from_metadata(env_name, injected_package)

    print(
        f"`{injected_package}` has been uninjected from `{env_name}`", file=sys.stderr
    )


def exit_if_not_installed(package: str):
    prefix = conda.conda_env_prefix(package)
    if not prefix.exists():
        print(f"`{package}` is not installed with condax", file=sys.stderr)
        sys.exit(0)


def remove_package(package: str):
    exit_if_not_installed(package)
    apps_to_unlink = _get_apps(package)
    remove_links(package, apps_to_unlink)
    conda.remove_conda_env(package)
    print(f"`{package}` has been removed from condax", file=sys.stderr)


def update_all_packages(is_forcing: bool = False):
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
                    f"  {shlex.quote(package_name)}",
                    f" {package_version} {package_build}",
                    f", using Python {python_version}" if python_version else "",
                ]
            )
            print(package_header)

            try:
                apps = _get_main_apps(package)
                executable_counts.update(apps)
                for app in apps:
                    print(f"    - {app}")

                name_injected_apps = _get_injected_apps_dict(package)
                for injected_package, injected_apps in name_injected_apps.items():
                    executable_counts.update(injected_apps)
                    name, version, build = conda.get_package_info(package, injected_package)
                    for app in injected_apps:
                        print(f"    - {app}  ({name} {version} {build})")


            except ValueError:
                print("    (no executables found)")

    # warn if duplicate executables are found
    duplicates = [name for (name, cnt) in executable_counts.items() if cnt > 1]
    if duplicates:
        print(f"\n[warning] The following executables are duplicated:")
        for name in duplicates:
            print(f"    * {name}")
        print()


def update_package(package: str, is_forcing: bool = False):
    exit_if_not_installed(package)
    try:
        executables_already_linked = set(conda.determine_executables_from_env(package))
        conda.update_conda_env(package)
        executables_linked_in_updated = set(
            conda.determine_executables_from_env(package)
        )

        to_create = executables_linked_in_updated - executables_already_linked
        to_delete = executables_already_linked - executables_linked_in_updated
        to_delete_apps = [path.name for path in to_delete]

        create_links(package, to_create, is_forcing)
        remove_links(package, to_delete_apps)
        print(f"{package} update successfully")

    except subprocess.CalledProcessError:
        print(f"`{package}` could not be updated", file=sys.stderr)
        print(f"removing and recreating instead", file=sys.stderr)

        remove_package(package)
        install_package(package, is_forcing=is_forcing)


def _create_metadata(package: str):
    """
    Create metadata file
    """
    apps = [p.name for p in conda.determine_executables_from_env(package)]
    main = metadata.MainPackage(package, apps)
    meta = metadata.CondaxMetaData(main)
    meta.save()


def _load_metadata(env: str) -> metadata.CondaxMetaData:
    meta = metadata.load(env)
    # For backward compatibility: metadata can be absent
    if meta is None:
        logging.info(f"Recreating condax_metadata.json in {env}...")
        _create_metadata(env)
        meta = metadata.load(env)
        if meta is None:
            raise ValueError(f"Failed to recreate condax_metadata.json in {env}")
    return meta


def _inject_to_metadata(env: str, injected: str, include_apps: bool = False):
    """
    Inject the package into the condax_metadata.json file for the env.
    """
    apps = [p.name for p in conda.determine_executables_from_env(env, injected)]
    pkg_to_inject = metadata.InjectedPackage(injected, apps, include_apps=include_apps)
    meta = _load_metadata(env)
    meta.uninject(injected)    # enable overwriting
    meta.inject(pkg_to_inject)
    meta.save()


def _uninject_from_metadata(env: str, injected: str):
    """
    Uninject the package from the condax_metadata.json file for the env.
    """
    meta = _load_metadata(env)
    meta.uninject(injected)
    meta.save()


def _get_injected_apps(env_name: str, injected_name: str) -> List[str]:
    """
    Return a list of apps for the given injected package.

    [NOTE] Get a non-empty list only if "include_apps" is True in the metadata.
    """
    meta = _load_metadata(env_name)
    result = [app for p in meta.injected_packages if p.name == injected_name and p.include_apps for app in p.apps]
    return result


def _get_main_apps(env_name: str) -> List[str]:
    """
    Return a list of all apps
    """
    meta = _load_metadata(env_name)
    return meta.main_package.apps


def _get_injected_apps_dict(env_name: str) -> Dict[str, List[str]]:
    """
    Return a list of all apps
    """
    meta = _load_metadata(env_name)
    return {p.name: p.apps for p in meta.injected_packages if p.include_apps}


def _get_apps(env_name: str) -> List[str]:
    """
    Return a list of all apps
    """
    meta = _load_metadata(env_name)
    return meta.main_package.apps + [app for p in meta.injected_packages if p.include_apps for app in p.apps]

