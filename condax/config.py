import os
from pathlib import Path
import shutil
from typing import List, Optional, Union

from condax.utils import to_path
import condax.condarc as condarc
import yaml

_config_filename = "config.yaml"
_localappdata_dir = os.environ.get("LOCALAPPDATA", "~\\AppData\\Local")

_xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
_default_config_unix = os.path.join(_xdg_config_home, "condax", _config_filename)
_default_config_windows = os.path.join(
    _localappdata_dir, "condax", "condax", _config_filename
)
_default_config = _default_config_windows if os.name == "nt" else _default_config_unix
DEFAULT_CONFIG = to_path(os.environ.get("CONDAX_CONFIG", _default_config))

_xdg_data_home = os.environ.get("XDG_DATA_HOME", "~/.local/share")
_default_prefix_dir_unix = os.path.join(_xdg_data_home, "condax", "envs")
_default_prefix_dir_win = os.path.join(_localappdata_dir, "condax", "condax", "envs")
_default_prefix_dir = (
    _default_prefix_dir_win if os.name == "nt" else _default_prefix_dir_unix
)
DEFAULT_PREFIX_DIR = to_path(os.environ.get("CONDAX_PREFIX_DIR", _default_prefix_dir))

DEFAULT_BIN_DIR = to_path(os.environ.get("CONDAX_BIN_DIR", "~/.local/bin"))

_channels_in_condarc = condarc.load_channels()
DEFAULT_CHANNELS = (
    os.environ.get("CONDAX_CHANNELS", " ".join(_channels_in_condarc)).strip().split()
)

CONDA_ENVIRONMENT_FILE = to_path("~/.conda/environments.txt")

conda_path = shutil.which("conda")
MAMBA_ROOT_PREFIX = (
    to_path(conda_path).parent.parent
    if conda_path is not None
    else to_path(os.environ.get("MAMBA_ROOT_PREFIX", "~/micromamba"))
)


# https://stackoverflow.com/questions/6198372/most-pythonic-way-to-provide-global-configuration-variables-in-config-py
class C:
    __conf = {
        "mamba_root_prefix": MAMBA_ROOT_PREFIX,
        "prefix_dir": DEFAULT_PREFIX_DIR,
        "bin_dir": DEFAULT_BIN_DIR,
        "channels": DEFAULT_CHANNELS,
    }

    @staticmethod
    def mamba_root_prefix() -> Path:
        return C.__conf["mamba_root_prefix"]

    @staticmethod
    def prefix_dir() -> Path:
        return C.__conf["prefix_dir"]

    @staticmethod
    def bin_dir() -> Path:
        return C.__conf["bin_dir"]

    @staticmethod
    def channels() -> List[str]:
        return C.__conf["channels"]

    @staticmethod
    def _set(name: str, value) -> None:
        if name in C.__conf:
            C.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")


def set_via_file(config_file: Union[str, Path]):
    """
    Set the object C from using a config file in YAML format.
    """
    config_file = to_path(config_file)
    if config_file.exists():
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        if not config:
            msg = f"""Config file does not contain config information: Remove {config_file} and try again"""
            raise ValueError(msg)

        # For compatibility with condax 0.0.5
        if "prefix_path" in config:
            prefix_dir = to_path(config["prefix_path"])
            C._set("prefix_dir", prefix_dir)

        # For compatibility with condax 0.0.5
        if "target_destination" in config:
            bin_dir = to_path(config["target_destination"])
            C._set("bin_dir", bin_dir)

        if "prefix_dir" in config:
            prefix_dir = to_path(config["prefix_dir"])
            C._set("prefix_dir", prefix_dir)

        if "bin_dir" in config:
            bin_dir = to_path(config["bin_dir"])
            C._set("bin_dir", bin_dir)

        if "channels" in config:
            channels = config["channels"]
            C._set("channels", channels)


def set_via_value(
    prefix_dir: Optional[Union[Path, str]] = None,
    bin_dir: Optional[Union[Path, str]] = None,
    channels: List[str] = [],
):
    """
    Set a part of values in the object C by passing values directly.
    """
    if prefix_dir:
        C._set("prefix_dir", to_path(prefix_dir))

    if bin_dir:
        C._set("bin_dir", to_path(bin_dir))

    if channels:
        C._set("channels", channels)
