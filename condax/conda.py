import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Set

from .config import CONFIG, is_windows


def ensure_dest_prefix() -> None:
    CONFIG.prefix_path.mkdir(parents=True, exist_ok=True)


def write_condarc_to_prefix(
    prefix: Path, channels: List[str], channel_priority: str = "strict"
) -> None:
    """Create a condarc with the channel priority used for installing the given tool.

    Earlier channels have higher priority"""
    with open(os.path.join(prefix, "condarc"), "w") as fo:
        fo.write(f"channel_priority: {channel_priority}\n")
        if channels:
            fo.write("channels:\n")
            for channel in channels:
                fo.write(f"  - {channel}\n")
        fo.write("\n")


def create_conda_environment(
    package: str, channels: Optional[List[str]] = None
) -> None:
    conda_exe = CONFIG.conda_executable
    assert conda_exe is not None
    prefix = conda_env_prefix(package)
    if channels is None:
        channels = CONFIG.channels

    channels_args: List[str] = []
    for c in channels:
        channels_args.extend(["--channel", c])

    subprocess.check_call(
        [
            str(conda_exe),
            "create",
            "--prefix",
            str(prefix),
            "--override-channels",
            *channels_args,
            "--quiet",
            "--yes",
            package,
        ]
    )

    write_condarc_to_prefix(prefix, channels)


def install_conda_packages(
    packages: List[str], prefix: Path, channels: Optional[List[str]] = None
):
    conda_exe = CONFIG.conda_executable
    assert conda_exe is not None
    if channels is None:
        channels = CONFIG.channels

    channels_args: List[str] = []
    if channels is not None:
        for c in channels:
            channels_args.extend(["--channel", c])

    subprocess.check_call(
        [
            str(conda_exe),
            "install",
            "--prefix",
            str(prefix),
            "--override-channels",
            *channels_args,
            "--quiet",
            "--yes",
            *packages,
        ]
    )


def remove_conda_env(package) -> None:
    conda_exe = CONFIG.conda_executable
    assert conda_exe is not None

    prefix = conda_env_prefix(package)
    subprocess.check_call(
        [str(conda_exe), "remove", "--prefix", str(prefix), "--all", "--yes"]
    )


def update_conda_env(package) -> None:
    conda_exe = CONFIG.conda_executable
    assert conda_exe is not None

    prefix = conda_env_prefix(package)
    subprocess.check_call(
        [str(conda_exe), "update", "--prefix", str(prefix), "--all", "--yes"]
    )


def conda_env_prefix(package: str) -> Path:
    return CONFIG.prefix_path / package


_RE_PKG_NAME = re.compile(r"^[a-zA-Z0-9._-]+")


def package_name(package_spec: str):
    """Get the package name from a package spec"""
    m = _RE_PKG_NAME.match(package_spec)
    assert m is not None
    return m.group(0)


def detemine_executables_from_env(
    package: str, env_prefix: Optional[Path] = None
) -> Set[Path]:
    if env_prefix is None:
        env_prefix = conda_env_prefix(package)
    name = package_name(package)
    metas = (env_prefix / "conda-meta").glob(f"{name}*.json")
    for path in metas:
        package_info = json.loads(path.read_text())
        if package_info["name"] == name:
            logging.debug("Candidate files: %s", package_info["files"])
            potential_executables: List[str] = [
                fn
                for fn in package_info["files"]
                if (
                    fn.startswith("bin/")
                    or fn.startswith("sbin/")
                    # They are Windows style path
                    or (
                        is_windows()
                        and (
                            fn.lower().startswith("scripts\\")
                            or fn.lower().startswith("library\\mingw-w64\\bin\\")
                            or re.match(r"library\\.*\\bin\\", fn.lower())
                        )
                    )
                )
            ]
            # TODO: Handle windows style paths
            break
    else:
        raise ValueError("Could not determine package files")

    pathext = os.environ.get("PATHEXT", "").split(";")
    executables: Set[Path] = set()
    for fn in potential_executables:
        abs_executable_path = env_prefix / fn
        # unix
        if os.access(abs_executable_path, os.X_OK):
            executables.add(abs_executable_path)
        # windows
        for ext in pathext:
            if ext and abs_executable_path.name.endswith(ext):
                executables.add(abs_executable_path)

    logging.debug(executables)
    return executables
