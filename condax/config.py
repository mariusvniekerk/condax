import os
import pathlib

import yaml


# TODO: Respect $XDG_DATA_HOME and $XDG_CONFIG_HOME environment variables
CONDAX_CONFIG_PATH = pathlib.Path("~/.config/condax/config.yaml").expanduser()
CONDAX_ENV_PREFIX_DIR = pathlib.Path("~/.local/share/condax/envs").expanduser()
CONDAX_LINK_DESTINATION = pathlib.Path("~/.local/bin").expanduser()

os.makedirs(CONDAX_ENV_PREFIX_DIR, exist_ok=True)
os.makedirs(CONDAX_LINK_DESTINATION, exist_ok=True)

DEFAULT_CHANNELS = ["conda-forge", "defaults"]


def set_defaults_if_absent(config_file: pathlib.Path) -> dict:
    """
    Load config file and set default values if they are not present.
    """
    if config_file.exists():
        with open(config_file, "r") as f:
            configs = yaml.safe_load(f)
    else:
        configs = dict()
    configs.setdefault("prefix_path", CONDAX_ENV_PREFIX_DIR)
    configs.setdefault("link_destination", CONDAX_LINK_DESTINATION)
    configs.setdefault("channels", DEFAULT_CHANNELS)
    return configs
