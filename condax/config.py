import os
import platform
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Generator, List, Optional

import yaml
from pydantic import ConfigDict, Field, field_validator

with warnings.catch_warnings():
    # requests which is a transitive dependency has some chatty warnings during import
    warnings.simplefilter("ignore", Warning)
    import requests  # noqa: F401

from ensureconda.api import ensureconda
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from _typeshed import StrPath


def is_windows() -> bool:
    return platform.system() == "Windows"


class Config(BaseSettings):
    prefix_path: Path = Path("~").expanduser() / ".condax"
    link_destination: Path = Path("~").expanduser() / ".local" / "bin"
    channels: List[str] = ["conda-forge", "defaults"]
    conda_executable: Optional[Path] = Field(
        default=ensureconda(
            mamba=True, micromamba=True, conda=True, conda_exe=True, no_install=True
        )
    )
    model_config = ConfigDict(env_prefix="CONDAX_")

    @field_validator("prefix_path", "link_destination", mode="before")
    @classmethod
    def ensure_prefix_path(cls, v: os.PathLike) -> Path:
        v = Path(v).expanduser()
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        v = v.resolve()
        return v

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


_condaxrc_path_list = [
    os.path.expanduser(os.path.join("~", ".condaxrc"))
]
if "CONDAXRC" in os.environ:
    _condaxrc_path_list = [os.environ["CONDAXRC"]] + _condaxrc_path_list
if "XDG_CONFIG_HOME" in os.environ:
    _condaxrc_path_list += [
        os.path.expanduser(
            os.path.join(os.environ["XDG_CONFIG_HOME"], "condax", "condaxrc")
        ),
        os.path.expanduser(
            os.path.join(os.environ["XDG_CONFIG_HOME"], "condax", ".condaxrc")
        ),
    ]
_condaxrc_path_list += [
    "/etc/condax/condaxrc",
    "/etc/condax/.condaxrc",
    "/var/lib/condax/condaxrc",
    "/var/lib/condax/.condaxrc"
]
_condaxrc_path_list = [x for x in _condaxrc_path_list if os.path.exists(x)]
if any(_condaxrc_path_list):
    _condaxrc_path = _condaxrc_path_list[0]
    with open(_condaxrc_path) as fo:
        CONFIG = Config(**yaml.safe_load(fo))
else:
    CONFIG = Config()
