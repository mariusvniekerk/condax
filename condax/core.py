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
import condax.config as config
from condax.config import C


def create_link(package: str, exe: Path, is_forcing: bool = False):
    micromamba_exe = conda.ensure_micromamba()
    executable_name = exe.name
    # FIXME: Enforcing conda (not mamba) for `conda run` for now
    prefix = conda.conda_env_prefix(package)
    if os.name == "nt":
        script_lines = [
            "@rem Entrypoint created by condax\n",
            f"@call {utils.quote(micromamba_exe)} run --prefix {utils.quote(prefix)} {utils.quote(exe)} %*\n",
        ]
    else:
        script_lines = [
            "#!/usr/bin/env bash\n",
            "\n",
            "# Entrypoint created by condax\n",
            f'{utils.quote(micromamba_exe)} run --prefix {utils.quote(prefix)} {utils.quote(exe)} "$@"\n',
        ]
        if utils.to_bool(os.environ.get("CONDAX_HIDE_EXITCODE", False)):
            # Let scripts to return exit code 0 constantly
            script_lines.append("exit 0\n")

    script_path = _get_wrapper_path(executable_name)
    if script_path.exists() and not is_forcing:
        user_input = input(f"{executable_name} already exists. Overwrite? (y/N) ")
        if user_input.strip().lower() not in ("y", "yes"):
            print(f"Skip installing app: {executable_name}...")
            return

    utils.unlink(script_path)
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

    if os.name == "nt":
        # FIXME: this is hand-waving for now
        for executable_name in app_names_to_unlink:
            link_path = _get_wrapper_path(executable_name)
            utils.unlink(link_path)
    else:
        for executable_name in app_names_to_unlink:
            link_path = _get_wrapper_path(executable_name)
            wrapper_env = wrapper.read_env_name(link_path)
            if wrapper_env is None:
                print(f"    {executable_name} \t (failed to get env)")
                utils.unlink(link_path)
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
                f"`{package}` is already installed. Run `condax install --force {package}` to force install.",
                file=sys.stderr,
            )
            sys.exit(1)

    conda.create_conda_environment(package, match_specs=match_specs)
    executables_to_link = conda.determine_executables_from_env(package)
    utils.mkdir(C.bin_dir())
    create_links(package, executables_to_link, is_forcing=is_forcing)
    _create_metadata(package)
    print(f"`{package}` has been installed by condax", file=sys.stderr)


def inject_package_to(
    env_name: str,
    injected_specs: List[str],
    is_forcing: bool = False,
    include_apps: bool = False,
):
    pairs = [utils.split_match_specs(spec) for spec in injected_specs]
    injected_packages, _ = zip(*pairs)
    pkgs_str = " and ".join(injected_packages)
    if not conda.has_conda_env(env_name):
        print(
            f"`{env_name}` does not exist; Abort injecting {pkgs_str} ...",
            file=sys.stderr,
        )
        sys.exit(1)

    # package match specifications
    # https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications


    conda.inject_to_conda_env(
        injected_specs,
        env_name,
    )

    # update the metadata
    _inject_to_metadata(env_name, injected_packages, include_apps)

    # Add links only if --include-apps is set
    if include_apps:
        for injected_pkg in injected_packages:
            executables_to_link = conda.determine_executables_from_env(
                env_name,
                injected_pkg,
            )
            create_links(env_name, executables_to_link, is_forcing=is_forcing)
    print(f"`Done injecting {pkgs_str} to `{env_name}`", file=sys.stderr)


def uninject_package_from(env_name: str, packages_to_uninject: List[str]):
    if not conda.has_conda_env(env_name):
        pkgs_str = " and ".join(packages_to_uninject)
        print(
            f"`The environment {env_name}` does not exist. Abort uninjecting `{pkgs_str}`...",
            file=sys.stderr,
        )
        sys.exit(1)

    already_injected = set(_get_injected_packages(env_name))
    to_uninject = set(packages_to_uninject)
    not_found = to_uninject - already_injected
    for pkg in not_found:
        print(
            f"`{pkg}` is absent in the `{env_name}` environment.",
            file=sys.stderr,
        )

    found = to_uninject & already_injected
    if not found:
        print(
            f"`No package is uninjected from {env_name}`",
            file=sys.stderr,
        )
        sys.exit(1)

    packages_to_uninject = sorted(found)
    conda.uninject_from_conda_env(packages_to_uninject, env_name)

    injected_app_names = [app for pkg in packages_to_uninject for app in _get_injected_apps(env_name, pkg)]
    remove_links(env_name, injected_app_names)
    _uninject_from_metadata(env_name, packages_to_uninject)

    pkgs_str = " and ".join(packages_to_uninject)
    print(
        f"`{pkgs_str}` has been uninjected from `{env_name}`", file=sys.stderr
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
    for package in _get_all_envs():
        update_package(package, is_forcing=is_forcing)


def list_all_packages(short=False, include_injected=False) -> None:
    if short:
        _list_all_packages_short(include_injected)
    elif include_injected:
        _list_all_packages_include_injected()
    else:
        _list_all_packages_default()


def _list_all_packages_short(include_injected: bool) -> None:
    """
    List packages with --short flag
    """
    for package in _get_all_envs():
        package_name, package_version, _ = conda.get_package_info(package)
        package_header = f"{package_name} {package_version}"
        print(package_header)
        if include_injected:
            injected_packages = _get_injected_packages(package_name)
            for injected_pkg in injected_packages:
                name, version, _ = conda.get_package_info(package_name, injected_pkg)
                print(f"    {name} {version}")


def _list_all_packages_default() -> None:
    """
    List packages without any flags
    """
    # messages follow pipx's text format
    _print_condax_dirs()

    executable_counts = collections.Counter()
    for package in _get_all_envs():
        _, python_version, _ = conda.get_package_info(package, "python")
        package_name, package_version, package_build = conda.get_package_info(package)

        package_header = "".join(
            [
                f"{shlex.quote(package_name)}",
                f" {package_version} {package_build}",
                f", using Python {python_version}" if python_version else "",
            ]
        )
        print(package_header)

        apps = _get_apps(package)
        executable_counts.update(apps)
        if not apps:
            print(f"    (No apps found for {package})")
        else:
            for app in apps:
                app = utils.strip_exe_ext(app)  # for windows
                print(f"    - {app}")
        print()

    # warn if duplicate of executables are found
    duplicates = [name for (name, cnt) in executable_counts.items() if cnt > 1]
    if duplicates:
        print(f"\n[warning] The following executables are duplicated:")
        for name in duplicates:
            # TODO: include the package environment linked from the executable
            print(f"    * {name}")
        print()


def _list_all_packages_include_injected():
    """
    List packages with --include-injected flag
    """
    # messages follow pipx's text format
    _print_condax_dirs()

    for env in _get_all_envs():
        _, python_version, _ = conda.get_package_info(env, "python")
        package_name, package_version, package_build = conda.get_package_info(env)

        package_header = "".join(
            [
                f"{package_name} {package_version} {package_build}",
                f", using Python {python_version}" if python_version else "",
            ]
        )
        print(package_header)

        apps = _get_main_apps(package_name)
        for app in apps:
            app = utils.strip_exe_ext(app)  # for windows
            print(f"    - {app}")

        names_injected_apps = _get_injected_apps_dict(package_name)
        for name, injected_apps in names_injected_apps.items():
            for app in injected_apps:
                app = utils.strip_exe_ext(app)  # for windows
                print(f"    - {app}  (from {name})")

        injected_packages = _get_injected_packages(package_name)
        if injected_packages:
            print("    Included packages:")

        for injected_pkg in injected_packages:
            name, version, build = conda.get_package_info(package_name, injected_pkg)
            print(f"        {name} {version} {build}")

        print()


def _print_condax_dirs() -> None:
    print(f"conda envs are in {C.prefix_dir()}")
    print(f"apps are exposed on your $PATH at {C.bin_dir()}")
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
        print(f"Failed to update `{package}`", file=sys.stderr)
        print(f"Recreating the environment...", file=sys.stderr)

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


def _inject_to_metadata(env: str, packages_to_inject: Iterable[str], include_apps: bool = False):
    """
    Inject the package into the condax_metadata.json file for the env.
    """
    meta = _load_metadata(env)
    for pkg in packages_to_inject:
        apps = [
            p.name for p in
            conda.determine_executables_from_env(env, pkg)
        ]
        pkg_to_inject = metadata.InjectedPackage(pkg, apps, include_apps=include_apps)
        meta.uninject(pkg)    # overwrites if necessary
        meta.inject(pkg_to_inject)
    meta.save()


def _uninject_from_metadata(env: str, packages_to_uninject: Iterable[str]):
    """
    Uninject the package from the condax_metadata.json file for the env.
    """
    meta = _load_metadata(env)
    for pkg in packages_to_uninject:
        meta.uninject(pkg)
    meta.save()


def _get_all_envs() -> List[str]:
    """
    Get all conda envs
    """
    utils.mkdir(C.prefix_dir())
    return sorted([pkg_dir.name for pkg_dir in C.prefix_dir().iterdir()])


def _get_injected_packages(env_name: str) -> List[str]:
    """
    Get the list of packages injected into the env.
    """
    meta = _load_metadata(env_name)
    return [p.name for p in meta.injected_packages]


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


def _get_wrapper_path(cmd_name: str) -> Path:
    p = C.bin_dir() / cmd_name
    if os.name == "nt":
        p = p.parent / (p.stem + ".bat")
    return p


def export_all_environments(out_dir: str) -> None:
    """Export all environments to a directory.
    """
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    print("Started exporting all environments to", p)

    envs = _get_all_envs()
    for env in envs:
        conda.export_env(env, p)
        _copy_metadata(env, p)

    print("Done.")


def _copy_metadata(env: str, p: Path):
    """Copy the condax_metadata.json file to the exported directory.
    """
    _from = metadata.CondaxMetaData.get_path(env)
    _to = p / f"{env}.json"
    shutil.copyfile(_from, _to, follow_symlinks=True)


def _overwrite_metadata(envfile: Path):
    """Copy the condax_metadata.json file to the exported directory.
    """
    env = envfile.stem
    _from = envfile
    _to = metadata.CondaxMetaData.get_path(env)
    if _to.exists():
        shutil.move(_to, _to.with_suffix(".bak"))
    shutil.copyfile(_from, _to, follow_symlinks=True)


def import_environments(in_dir: str, is_forcing: bool) -> None:
    """Import all environments from a directory.
    """
    p = Path(in_dir)
    print("Started importing environments in", p)
    for envfile in p.glob("*.yml"):
        env = envfile.stem
        if conda.has_conda_env(env):
            if is_forcing:
                remove_package(env)
            else:
                print(f"Environment {env} already exists. Skipping...")
                continue

        conda.import_env(envfile)

        metafile = p / (env + ".json")
        _overwrite_metadata(metafile)
        _recreate_links(env)

    print("Done.")


def _get_executables_to_link(env: str) -> List[Path]:
    """
    Return a list of executables to link.
    """
    meta = _load_metadata(env)

    env = meta.main_package.name
    result = conda.determine_executables_from_env(env)

    injected_packages = meta.injected_packages
    for pkg in injected_packages:
        if pkg.include_apps:
            result += conda.determine_executables_from_env(env, pkg.name)

    return result


def _recreate_links(env: str) -> None:
    """
    Recreate the links for the given environment.
    """
    executables_to_link = _get_executables_to_link(env)
    create_links(env, executables_to_link, is_forcing=True)


def _recreate_all_links():
    """
    Recreate the links for all environments.
    """
    envs = _get_all_envs()
    for env in envs:
        _recreate_links(env)


def _prune_links():
    to_apps = {env: _get_apps(env) for env in _get_all_envs()}

    utils.mkdir(C.bin_dir())
    links = C.bin_dir().glob("*")
    for link in links:
        if link.is_symlink() and (not link.exists()):
            link.unlink()

        if not wrapper.is_wrapper(link):
            continue

        target_env = wrapper.read_env_name(link)
        if target_env is None:
            logging.info(f"Failed to read env name from {link}")
            continue

        exec_name = utils.to_body_ext(link.name)
        valid_apps = to_apps.get(target_env, [])
        if exec_name not in valid_apps:
            print("  ... removing", link)
            link.unlink()


def _add_to_conda_env_list() -> None:
    """Add condax environment prefixes to ~/.conda/environments.txt if not already there.
    """
    envs = _get_all_envs()
    prefixe_str_set = {str(conda.conda_env_prefix(env)) for env in envs}
    lines = set()

    envs_txt = config.CONDA_ENVIRONMENT_FILE
    if envs_txt.exists():
        with envs_txt.open() as f:
            lines = {line.strip() for line in f.readlines()}

    missing = sorted(prefixe_str_set - lines)
    if missing:
        envs_txt.parent.mkdir(exist_ok=True)
        with envs_txt.open("a") as f:
            print("", file=f)
            print("\n".join(missing), file=f)


def fix_links():
    """
    Run the repair lin.
    """
    utils.mkdir(C.bin_dir())

    print(f"Repairing links in the BIN_DIR: {C.bin_dir()}...")
    _prune_links()
    _recreate_all_links()
    _add_to_conda_env_list()
    print("  ... Done.")
