import io
import json
import logging
import os
import shlex
import shutil
import stat
import subprocess
from pathlib import Path
import sys
import tarfile
from typing import Iterable, List, Optional, Tuple, Union

import requests

from condax.config import C
from condax.utils import to_path
import condax.utils as utils


def ensure_conda():
    execs = ["mamba", "conda"]
    for conda_exec in execs:
        conda_path = shutil.which(conda_exec)
        if conda_path is not None:
            return conda_path

    logging.info("No existing conda installation found.  Installing the standalone")
    return setup_conda()


def ensure_micromamba():
    execs = ["micromamba"]
    for conda_exec in execs:
        conda_path = shutil.which(conda_exec)
        if conda_path is not None:
            return conda_path

    logging.info("No existing conda installation found.  Installing the standalone")
    return setup_micromamba()


def setup_conda():
    url = utils.get_conda_url()
    resp = requests.get(url, allow_redirects=True)
    resp.raise_for_status()
    utils.mkdir(C.bin_dir())
    target_filename = C.bin_dir() / "conda.exe"
    with open(target_filename, "wb") as fo:
        fo.write(resp.content)
    st = os.stat(target_filename)
    os.chmod(target_filename, st.st_mode | stat.S_IXUSR)
    return target_filename


def setup_micromamba() -> Path:
    utils.mkdir(C.bin_dir())
    umamba_exe = C.bin_dir() / "micromamba"
    _download_extract_micromamba(umamba_exe)
    return umamba_exe


def _download_extract_micromamba(umamba_dst: Path):
    url = utils.get_micromamba_url()
    print(f"Downloading micromamba from {url}")
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()

    utils.mkdir(umamba_dst.parent)
    tarfile_obj = io.BytesIO(response.content)
    with tarfile.open(fileobj=tarfile_obj) as tar, open(umamba_dst, "wb") as f:
        extracted = tar.extractfile("bin/micromamba")
        if extracted:
            shutil.copyfileobj(extracted, f)

    st = os.stat(umamba_dst)
    os.chmod(umamba_dst, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


## Need to activate if using micromamba as drop-in replacement
# def _activate_umamba(umamba_path: Path) -> None:
#     print("Activating micromamba")
#     _subprocess_run(
#         f'eval "$({umamba_path} shell hook --shell posix --prefix {C.mamba_root_prefix()})"',
#         shell=True,
#     )


def create_conda_environment(package: str, match_specs=""):
    conda_exe = ensure_conda()
    prefix = conda_env_prefix(package)

    channels = C.channels()
    channels_args = [x for c in channels for x in ["--channel", c]]

    _subprocess_run(
        [
            conda_exe,
            "create",
            "--prefix",
            prefix,
            "--override-channels",
            *channels_args,
            "--quiet",
            "--yes",
            shlex.quote(package + match_specs),
        ]
    )


def inject_to_conda_env(specs: Iterable[str], env_name: str):

    conda_exe = ensure_conda()
    prefix = conda_env_prefix(env_name)
    channels_args = [x for c in C.channels() for x in ["--channel", c]]
    specs_args = [shlex.quote(spec) for spec in specs]

    res = _subprocess_run(
        [
            conda_exe,
            "install",
            "--prefix",
            prefix,
            "--override-channels",
            *channels_args,
            "--quiet",
            "--yes",
            *specs_args,
        ]
    )


def uninject_from_conda_env(packages: Iterable[str], env_name: str):
    conda_exe = ensure_conda()
    prefix = conda_env_prefix(env_name)

    _subprocess_run(
        [
            conda_exe,
            "uninstall",
            "--prefix",
            prefix,
            "--quiet",
            "--yes",
            *packages,
        ]
    )


def remove_conda_env(package: str):
    conda_exe = ensure_conda()

    _subprocess_run(
        [conda_exe, "remove", "--prefix", conda_env_prefix(package), "--all", "--yes"]
    )


def update_conda_env(package: str):
    conda_exe = ensure_conda()

    _subprocess_run(
        [conda_exe, "update", "--prefix", conda_env_prefix(package), "--all", "--yes"]
    )


def has_conda_env(package: str) -> bool:
    # TODO: check some properties of a conda environment
    p = conda_env_prefix(package)
    return p.exists() and p.is_dir()


def conda_env_prefix(package: str) -> Path:
    return C.prefix_dir() / package


def get_package_info(package, specific_name=None) -> Tuple[str, str, str]:
    env_prefix = conda_env_prefix(package)
    package_name = package if specific_name is None else specific_name
    conda_meta_dir = env_prefix / "conda-meta"
    try:
        for file_name in conda_meta_dir.glob(f"{package_name}*.json"):
            with open(file_name, "r") as fo:
                package_info = json.load(fo)
                if package_info["name"] == package_name:
                    name: str = package_info["name"]
                    version: str = package_info["version"]
                    build: str = package_info["build"]
                    return (name, version, build)
    except ValueError:
        logging.info(
            "".join(
                [
                    f"Could not retrieve package info: {package}",
                    f" - {specific_name}" if specific_name else "",
                ]
            )
        )

    return ("", "", "")


def determine_executables_from_env(
    package: str, injected_package: Optional[str] = None
) -> List[Path]:
    def is_good(p: Union[str, Path]) -> bool:
        p = to_path(p)
        return p.parent.name in ("bin", "sbin", "scripts", "Scripts")

    env_prefix = conda_env_prefix(package)
    target_name = injected_package if injected_package else package

    conda_meta_dir = env_prefix / "conda-meta"
    for file_name in conda_meta_dir.glob(f"{target_name}*.json"):
        with open(file_name, "r") as fo:
            package_info = json.load(fo)
            if package_info["name"] == target_name:
                potential_executables: List[str] = [
                    fn
                    for fn in package_info["files"]
                    if (fn.startswith("bin/") and is_good(fn))
                    or (fn.startswith("sbin/") and is_good(fn))
                    # They are Windows style path
                    or (fn.lower().startswith("scripts") and is_good(fn))
                    or (fn.lower().startswith("library") and is_good(fn))
                ]
                break
    else:
        raise ValueError(
            f"Could not determine package files: {package} - {injected_package}"
        )

    executables = set()
    for fn in potential_executables:
        exec_path = env_prefix / fn
        if utils.is_executable(exec_path):
            executables.add(exec_path)
    return sorted(executables)


def _get_conda_package_dirs() -> List[Path]:
    """
    Get the conda's global package directories.

    Equivalent to running `conda info --json | jq '.pkgs_dirs'`
    """
    conda_exe = ensure_conda()
    res = subprocess.run([conda_exe, "info", "--json"], capture_output=True)
    if res.returncode != 0:
        return []

    d = json.loads(res.stdout.decode())
    return [to_path(p) for p in d["pkgs_dirs"]]


def _get_dependencies(package: str, pkg_dir: Path) -> List[str]:
    """
    A helper function: Get a list of dependent packages for a given package.
    """
    name, version, build = get_package_info(package)
    p = pkg_dir / f"{name}-{version}-{build}/info/index.json"
    if not p.exists():
        return []

    with open(p, "r") as fo:
        index = json.load(fo)

    if not index or "depends" not in index:
        return []

    return index["depends"]


def get_dependencies(package: str) -> List[str]:
    """
    Get a list of dependent packages of a given package.

    Returns a list of package match specifications.

    https://stackoverflow.com/questions/26101972/how-to-identify-conda-package-dependents
    """
    pkg_dirs = _get_conda_package_dirs()
    result = [x for pkg_dir in pkg_dirs for x in _get_dependencies(package, pkg_dir)]
    return result


def _subprocess_run(
    args: Union[str, List[Union[str, Path]]], **kwargs
) -> subprocess.CompletedProcess:
    """
    Run a subprocess and return the CompletedProcess object.
    """
    env = os.environ.copy()
    env.update({"MAMBA_NO_BANNER": "1"})
    res = subprocess.run(args, **kwargs, env=env)
    if res.returncode != 0:
        sys.exit(res.returncode)
    return res


def export_env(env_name: str, out_dir: Path):
    """Export an environment to a conda environment file."""
    conda_exe = ensure_conda()
    prefix = conda_env_prefix(env_name)
    filepath = out_dir / f"{env_name}.yml"
    _subprocess_run(
        [
            conda_exe,
            "env",
            "export",
            "--no-builds",
            "--prefix",
            prefix,
            "--file",
            filepath,
        ]
    )


def import_env(env_file: Path, is_forcing: bool = False):
    """Import an environment from a conda environment file."""
    conda_exe = ensure_conda()
    force_args = ["--force"] if is_forcing else []
    env_name = env_file.stem
    prefix = conda_env_prefix(env_name)
    _subprocess_run(
        [
            conda_exe,
            "env",
            "create",
            *force_args,
            "--prefix",
            prefix,
            "--file",
            env_file,
        ]
    )
