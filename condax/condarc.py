from pathlib import Path
from typing import List

import yaml


DEFAULT_CHANNELS = ["conda-forge", "defaults"]

# Search only ~/.mambarc and ~/.condarc for now
# although conda looks for many locations.
# https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/use-condarc.html#searching-for-condarc
PATHS = [
    Path.home() / ".mambarc",
    Path.home() / ".condarc",
]


def load_channels() -> List[str]:
    """Load 'channels' from PATHS. Earlier paths have precedence."""

    for p in PATHS:
        if p.exists():
            channels = _load_yaml(p)
            if channels:
                return channels

    return DEFAULT_CHANNELS


def _load_yaml(path: Path) -> List[str]:
    with open(path, "r") as f:
        d = yaml.safe_load(f)

    res = d.get("channels", [])
    return res
