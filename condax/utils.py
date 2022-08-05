import os
from pathlib import Path
import platform
from typing import List, Tuple, Union
import re
import urllib.parse


pat = re.compile(r"<=|>=|==|!=|<|>|=")


def split_match_specs(package_with_specs: str) -> Tuple[str, str]:
    """
    Split package match specification into (<package name>, <rest>)
    https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications

    Assume the argument `package_with_specs` is unquoted.

    >>> split_match_specs("numpy=1.11")
    ("numpy", "=1.11")

    >>> split_match_specs("numpy==1.11")
    ("numpy", "==1.11")

    >>> split_match_specs("numpy>1.11")
    ("numpy", ">1.11")

    >>> split_match_specs("numpy=1.11.1|1.11.3")
    ("numpy", "=1.11.1|1.11.3")

    >>> split_match_specs("numpy>=1.8,<2")
    ("numpy", ">=1.8,<2")

    >>> split_match_specs("numpy")
    ("numpy", "")
    """
    name, *_ = pat.split(package_with_specs)
    # replace with str.removeprefix() once Python>=3.9 is assured
    match_specs = package_with_specs[len(name) :]
    return name.strip(), match_specs.strip()


def to_path(path: Union[str, Path]) -> Path:
    """
    Convert a string to a pathlib.Path object.
    """
    return Path(path).expanduser().resolve()


def mkdir(path: Union[Path, str]) -> None:
    """mkdir -p path"""
    to_path(path).mkdir(exist_ok=True, parents=True)


def quote(path: Union[Path, str]) -> str:
    return f'"{str(path)}"'


def is_executable(path: Path) -> bool:
    """
    Check if a file is executable.
    """
    if not path.is_file():
        return False

    if os.name == "nt":
        pathexts = [
            ext.strip().lower()
            for ext in os.environ.get("PATHEXT", "").split(os.pathsep)
        ]
        ext = path.suffix.lower()
        return ext and (ext in pathexts)

    return os.access(path, os.X_OK)


def strip_exe_ext(filename: str) -> str:
    """
    Strip the executable extension from a filename.
    """
    if filename.lower().endswith(".exe"):
        return filename[:-4]
    return filename


def to_body_ext(wrapper_name: str) -> str:
    """
    Convert a wrapper script to a body script.
    """
    return _replace_suffix(wrapper_name, ".bat", ".exe")


def to_wrapper_ext(body_name: str) -> str:
    """
    Convert a wrapper script to a body script.
    """
    return _replace_suffix(body_name, ".exe", ".bat")


def _replace_suffix(filename: str, from_: str, to_: str) -> str:
    """
    Replace the extension suffix of a filepath.
    """
    p = Path(filename)
    if p.suffix == from_:
        return str(p.with_suffix(to_))
    return filename


def unlink(path: Path):
    """Replacement to Path.unlink(missing_ok=True)

    as it is unavailable in Python < 3.8.
    """
    if path.exists():
        path.unlink()


def get_micromamba_url() -> str:
    """
    Get the URL of the latest micromamba release.
    """
    base = "https://micro.mamba.pm/api/micromamba/"
    if platform.system() == "Linux" and platform.machine() == "x86_64":
        subdir = "linux-64/latest"
    elif platform.system() == "Darwin":
        subdir = "osx-64/latest"
    else:
        # TODO: Support windows here
        raise ValueError(f"Unsupported platform: {platform.system()}")

    url = urllib.parse.urljoin(base, subdir)
    return url


def get_conda_url() -> str:
    """
    Get the URL of the latest micromamba release.
    """
    base = "https://repo.anaconda.com/pkgs/misc/conda-execs"
    if platform.system() == "Linux" and platform.machine() == "x86_64":
        subdir = "conda-latest-linux-64.exe"
    elif platform.system() == "Darwin":
        subdir = "conda-latest-osx-64.exe"
    else:
        # TODO: Support windows here
        raise ValueError(f"Unsupported platform: {platform.system()}")

    url = urllib.parse.urljoin(base, subdir)
    return url
