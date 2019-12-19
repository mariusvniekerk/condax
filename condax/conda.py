import glob
import json
import logging
import os
import platform
import shutil
import stat
import subprocess

import requests

from .config import CONDA_ENV_PREFIX_PATH


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
        raise ValueError(f"Unsupported platform: {platform.system()}")

    resp = requests.get(f"{conda_exe_prefix}/{conda_exe_file}", allow_redirects=True)
    resp.raise_for_status()
    target_filename = os.path.expanduser("~/.local/conda.exe")
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
            f"{CONDA_ENV_PREFIX_PATH}/{package}",
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
        [
            conda_exe,
            "remove",
            "--prefix",
            f"{CONDA_ENV_PREFIX_PATH}/{package}",
            "--all",
        ]
    )


def conda_env_prefix(package):
    return f"{CONDA_ENV_PREFIX_PATH}/{package}"


def detemine_executables_from_env(package):
    env_prefix = conda_env_prefix(package)

    for file_name in glob.glob(f"{env_prefix}/conda-meta/{package}*.json"):
        with open(file_name, "r") as fo:
            package_info = json.load(fo)
            if package_info["name"] == package:
                potential_executables = [
                    fn
                    for fn in package_info["files"]
                    if fn.startswith("bin/") or fn.startswith("sbin/")
                ]
                break
    else:
        raise ValueError("Could not determine package files")

    executables = []
    for fn in potential_executables:
        abs_executable_path = f"{env_prefix}/{fn}"
        if os.access(abs_executable_path, os.X_OK):
            executables.append(abs_executable_path)

    return executables
