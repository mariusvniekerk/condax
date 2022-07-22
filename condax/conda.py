import json
import logging
import os
import platform
import shlex
import shutil
import stat
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Union

import requests

from condax.config import C
from condax.paths import mkpath
from condax.utils import to_path


def ensure_conda(mamba_ok=True):
    execs = ["conda", "conda.exe"]
    if mamba_ok:
        execs.insert(0, "mamba")

    for conda_exec in execs:
        conda_path = shutil.which(conda_exec)
        if conda_path is not None:
            return conda_path

    logging.info("No existing conda installation found.  Installing the standalone")
    return install_conda_exe()


def install_conda_exe():
    conda_exe_prefix = "https://repo.anaconda.com/pkgs/misc/conda-execs"
    if platform.system() == "Linux":
        conda_exe_file = "conda-latest-linux-64.exe"
    elif platform.system() == "Darwin":
        conda_exe_file = "conda-latest-osx-64.exe"
    else:
        # TODO: Support windows here
        raise ValueError(f"Unsupported platform: {platform.system()}")

    resp = requests.get(f"{conda_exe_prefix}/{conda_exe_file}", allow_redirects=True)
    resp.raise_for_status()
    mkpath(C.bin_dir())
    target_filename = C.bin_dir() / "conda.exe"
    with open(target_filename, "wb") as fo:
        fo.write(resp.content)
    st = os.stat(target_filename)
    os.chmod(target_filename, st.st_mode | stat.S_IXUSR)
    return target_filename


def write_condarc_to_prefix(prefix: Path, channel_priority: str = "strict"):
    """Create a condarc with the channel priority used for installing the given tool.

    Earlier channels have higher priority"""
    channels = C.channels()
    with open(prefix / "condarc", "w") as fo:
        fo.write(f"channel_priority: {channel_priority}\n")
        if channels:
            fo.write("channels:\n")
        for channel in channels:
            fo.write(f"  - {channel}\n")
        fo.write("\n")


def create_conda_environment(package: str, match_specs=""):
    conda_exe = ensure_conda()
    prefix = conda_env_prefix(package)

    channels = C.channels()
    channels_args = [x for c in channels for x in ["--channel", c]]

    subprocess.check_call(
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

    write_condarc_to_prefix(prefix)


def inject_to_conda_env(package: str, env_name: str, match_specs=""):

    conda_exe = ensure_conda()
    prefix = conda_env_prefix(env_name)
    channels_args = [x for c in C.channels() for x in ["--channel", c]]

    subprocess.check_call(
        [
            conda_exe,
            "install",
            "--prefix",
            prefix,
            "--override-channels",
            *channels_args,
            "--quiet",
            "--yes",
            shlex.quote(package + match_specs),
        ]
    )


def uninject_from_conda_env(package: str, env_name: str):
    conda_exe = ensure_conda()
    prefix = conda_env_prefix(env_name)

    subprocess.check_call(
        [
            conda_exe,
            "uninstall",
            "--prefix",
            prefix,
            "--quiet",
            "--yes",
            package,
        ]
    )


def remove_conda_env(package: str):
    conda_exe = ensure_conda()

    subprocess.check_call(
        [conda_exe, "remove", "--prefix", conda_env_prefix(package), "--all", "--yes"]
    )


def update_conda_env(package: str):
    conda_exe = ensure_conda()

    subprocess.check_call(
        [conda_exe, "update", "--prefix", conda_env_prefix(package), "--all", "--yes"]
    )


def has_conda_env(package: str) -> bool:
    return conda_env_prefix(package).exists()


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
                potential_executables = [
                    fn
                    for fn in package_info["files"]
                    if (fn.startswith("bin/") and is_good(fn))
                    or (fn.startswith("sbin/") and is_good(fn))
                    or (fn.lower().startswith("scripts/") and is_good(fn))
                ]
                # TODO: Handle windows style paths
                break
    else:
        raise ValueError("Could not determine package files")

    pathext = os.environ.get("PATHEXT", "").split(";")
    executables = set()
    for fn in potential_executables:
        abs_executable_path = env_prefix / fn
        # unix
        if os.access(abs_executable_path, os.X_OK):
            executables.add(abs_executable_path)
        # windows
        for ext in pathext:
            if ext and abs_executable_path.endswith(ext):
                executables.add(abs_executable_path)

    return sorted(executables)
