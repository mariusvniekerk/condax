import os

import yaml

_condaxrc_path = os.path.expanduser(os.path.join("~", ".config", "condax", "config.yaml"))
if os.path.exists(_condaxrc_path):
    with open(_condaxrc_path, "r") as fo:
        _config = yaml.safe_load(fo)
else:
    _config = {}

_config.setdefault("prefix_path", os.path.join("~", ".local", "share", "condax", "envs"))
_config.setdefault(
    "link_destination", os.path.expanduser(os.path.join("~", ".local", "bin"))
)
_config.setdefault("channels", ["conda-forge", "defaults"])


CONDA_ENV_PREFIX_PATH = os.path.expanduser(_config["prefix_path"])
CONDAX_LINK_DESTINATION = os.path.expanduser(_config["link_destination"])
DEFAULT_CHANNELS = _config["channels"]

os.makedirs(CONDA_ENV_PREFIX_PATH, exist_ok=True)
os.makedirs(CONDAX_LINK_DESTINATION, exist_ok=True)
