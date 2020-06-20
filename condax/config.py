import os

import yaml
import pathlib

_condaxrc_path = pathlib.Path.home() / ".condaxrc"
if _condaxrc_path.exists():
    with _condaxrc_path.open("r") as fo:
        _config = yaml.safe_load(fo)
else:
    _config = {}

_config.setdefault("prefix_path", str(pathlib.Path.home() / ".condax"))
_config.setdefault(
    "link_destination", str(pathlib.Path.home() / ".local" / "bin")
)
_config.setdefault("channels", ["conda-forge", "defaults"])


CONDA_ENV_PREFIX_PATH = os.path.expanduser(_config["prefix_path"])
CONDAX_LINK_DESTINATION = os.path.expanduser(_config["link_destination"])
DEFAULT_CHANNELS = _config["channels"]
