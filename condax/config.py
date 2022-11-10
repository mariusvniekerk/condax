import os
import platform
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Optional

import yaml
from pydantic import BaseSettings, Field

with warnings.catch_warnings():
    # requests which is a transitive dependency has some chatty warnings during import
    warnings.simplefilter("ignore", Warning)
    import requests  # noqa: F401

from ensureconda.api import ensureconda

if TYPE_CHECKING:
    from _typeshed import StrPath


def is_windows() -> bool:
    return platform.system() == "Windows"


class Config(BaseSettings):
    prefix_path: Path = Path("~").expanduser() / ".condax"
    link_destination: Path = Path("~").expanduser() / ".local" / "bin"
    channels = ["conda-forge", "defaults"]
    conda_executable: Optional[Path] = Field(
        default=ensureconda(
            mamba=True, micromamba=True, conda=True, conda_exe=True, no_install=True
        )
    )

    class Config:
        env_prefix = "CONDAX_"

    def ensure_conda_executable(self, require_mamba: bool = True):
        def candidates() -> "Generator[Optional[StrPath], None, None]":
            yield ensureconda(
                mamba=True,
                micromamba=True,
                conda=False,
                conda_exe=False,
                no_install=True,
            )
            if not require_mamba:
                yield ensureconda(
                    mamba=False,
                    micromamba=False,
                    conda=True,
                    conda_exe=True,
                    no_install=True,
                )
            yield ensureconda(
                mamba=True,
                micromamba=True,
                no_install=False,
                conda=False,
                conda_exe=False,
            )
            if not require_mamba:
                yield ensureconda(
                    mamba=False,
                    micromamba=False,
                    no_install=False,
                    conda=True,
                    conda_exe=True,
                )

        for c in candidates():
            if c is not None:
                self.conda_executable = Path(c)
                return
        else:
            raise RuntimeError("Could not find conda executable")


_condaxrc_path = os.path.expanduser(os.path.join("~", ".condaxrc"))
if os.path.exists(_condaxrc_path):
    with open(_condaxrc_path) as fo:
        CONFIG = Config(**yaml.safe_load(fo))
else:
    CONFIG = Config()
