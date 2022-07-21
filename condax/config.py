import os
import pathlib
from typing import List, Optional

import yaml


Path = pathlib.Path

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", "~/.config")
DEFAULT_CONFIG = os.environ.get("CONDAX_CONFIG", os.path.join(XDG_CONFIG_HOME, "condax/config.yaml"))

XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", "~/.local/share")
DEFAULT_PREFIX_DIR = Path(
    os.environ.get("CONDAX_PREFIX_DIR", os.path.join(XDG_DATA_HOME, "condax/envs"))
).expanduser()
DEFAULT_BIN_DIR = Path(
    os.environ.get("CONDAX_BIN_DIR", "~/.local/bin")
).expanduser()
DEFAULT_CHANNELS = ["conda-forge", "defaults"]


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


def set_via_file(config_file: Path):
    """
    Load config file and set default values if they are not present.
    """
    config = dict()
    if config_file.exists():
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

    if "prefix_path" in config:
        refix_dir = Path(config["prefix_path"]).expanduser()
        C._set("prefix_dir", refix_dir)

    if "bin_path" in config:
        bin_dir = Path(config["bin_path"]).expanduser()
        C._set("bin_dir", bin_dir)

    if "channels" in config:
        channels = config["channels"]
        C._set("channels", channels)


def set_via_value(
    prefix_dir: Optional[Path] = None,
    bin_dir: Optional[Path] = None,
    channels: List[str] = []):  # type: ignore
    """
    Set default values via arguments.
    """
    if prefix_dir:
        C._set("prefix_dir", prefix_dir)

    if bin_dir:
        C._set("bin_dir", bin_dir)

    if channels:
        C._set("channels", channels)
