import os
import pathlib
from typing import List, Optional, Union

import yaml


Path = pathlib.Path

_XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", "~/.config")
DEFAULT_CONFIG = os.environ.get("CONDAX_CONFIG", os.path.join(_XDG_CONFIG_HOME, "condax/config.yaml"))

_XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", "~/.local/share")
DEFAULT_PREFIX_DIR = Path(
    os.environ.get("CONDAX_PREFIX_DIR", os.path.join(_XDG_DATA_HOME, "condax/envs"))
).expanduser().resolve()
DEFAULT_BIN_DIR = Path(
    os.environ.get("CONDAX_BIN_DIR", "~/.local/bin")
).expanduser().resolve()
DEFAULT_CHANNELS = os.environ.get("CONDAX_CHANNELS", "conda-forge  defaults").split()


# https://stackoverflow.com/questions/6198372/most-pythonic-way-to-provide-global-configuration-variables-in-config-py
class C:
    __conf = {
        "prefix_dir": DEFAULT_PREFIX_DIR,
        "bin_dir": DEFAULT_BIN_DIR,
        "channels": DEFAULT_CHANNELS,
    }

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
    def _set(name: str, value):
        if name in C.__conf:
            C.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")


def set_via_file(config_file: Union[str, Path]):
    """
    Set the object C from using a config file in YAML format.
    """
    config_file = Path(config_file)
    if config_file.exists():
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        if not config:
            msg = f"""Config file does not contain config information: Remove {config_file} and try again"""
            raise ValueError(msg)

        # For compatibility with condax 0.0.5
        if "prefix_path" in config:
            prefix_dir = Path(config["prefix_path"]).expanduser().resolve()
            C._set("prefix_dir", prefix_dir)

        # For compatibility with condax 0.0.5
        if "target_destination" in config:
            bin_dir = Path(config["target_destination"]).expanduser().resolve()
            C._set("bin_dir", bin_dir)

        if "prefix_dir" in config:
            prefix_dir = Path(config["prefix_dir"]).expanduser().resolve()
            C._set("prefix_dir", prefix_dir)

        if "bin_dir" in config:
            bin_dir = Path(config["bin_dir"]).expanduser().resolve()
            C._set("bin_dir", bin_dir)

        if "channels" in config:
            channels = config["channels"]
            C._set("channels", channels)


def set_via_value(
    prefix_dir: Optional[Union[Path, str]] = None,
    bin_dir: Optional[Union[Path, str]] = None,
    channels: List[str] = []):  # type: ignore
    """
    Set a part of values in the object C by passing values directly.
    """
    if prefix_dir:
        C._set("prefix_dir", Path(prefix_dir).expanduser().resolve())

    if bin_dir:
        C._set("bin_dir", Path(bin_dir).expanduser().resolve())

    if channels:
        C._set("channels", channels)

