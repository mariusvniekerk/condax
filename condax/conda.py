import glob
import json
import logging
import os
import platform
import shutil
import stat
import subprocess

import requests

from .config import CONDA_ENV_PREFIX_PATH, CONDAX_LINK_DESTINATION
from .paths import mkpath


def ensure_conda():
    conda_executable = shutil.which("conda")
    if conda_executable:
        return conda_executable

    conda_executable = shutil.which("conda.exe")
    if conda_executable:
        return conda_executable

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
    mkpath(CONDAX_LINK_DESTINATION)
    target_filename = os.path.expanduser(os.path.join(CONDAX_LINK_DESTINATION))
    with open(target_filename, "wb") as fo:
        fo.write(resp.content)
    st = os.stat(target_filename)
    os.chmod(target_filename, st.st_mode | stat.S_IXUSR)
    return target_filename


def ensure_dest_prefix():
    if not os.path.exists(CONDA_ENV_PREFIX_PATH):
        os.mkdir(CONDA_ENV_PREFIX_PATH)


def create_conda_environment(package):
    conda_exe = ensure_conda()

    subprocess.check_call(
        [
            conda_exe,
            "create",
            "--prefix",
            os.path.join(CONDA_ENV_PREFIX_PATH, package),
            "--override-channels",
            # TODO: allow configuring this
            "--channel",
            "conda-forge",
            "--channel",
            "defaults",
            "--quiet",
            package,
        ]
    )


def remove_conda_env(package):
    conda_exe = ensure_conda()

    subprocess.check_call(
        [conda_exe, "remove", "--prefix", conda_env_prefix(package), "--all",]
    )


def update_conda_env(package):
    conda_exe = ensure_conda()

    subprocess.check_call(
        [conda_exe, "update", "--prefix", conda_env_prefix(package), "--all",]
    )


def conda_env_prefix(package):
    return os.path.join(CONDA_ENV_PREFIX_PATH, package)


def detemine_executables_from_env(package):
    env_prefix = conda_env_prefix(package)

    glob_pattern = os.path.join(env_prefix, "conda-meta", f"{package}*.json")
    for file_name in glob.glob(glob_pattern):
        with open(file_name, "r") as fo:
            package_info = json.load(fo)
            if package_info["name"] == package:
                potential_executables = [
                    fn
                    for fn in package_info["files"]
                    if fn.startswith("bin/") or fn.startswith("sbin/")
                ]
                # TODO: Handle windows style paths
                break
    else:
        raise ValueError("Could not determine package files")

    executables = []
    for fn in potential_executables:
        abs_executable_path = f"{env_prefix}/{fn}"
        if os.access(abs_executable_path, os.X_OK):
            executables.append(abs_executable_path)

    return executables
