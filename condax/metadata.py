from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, Field


class PrefixMetadata(BaseModel):
    prefix: Path
    links: Dict[Path, Path] = Field(
        default_factory=dict,
        description="Key is the local executable, value is the link path",
    )
    injected_packages: List[str] = Field(
        default_factory=list,
        description="Extra packages to injected into in the environment",
    )
    injected_packages_with_apps: List[str] = Field(
        default_factory=list,
        description="Extra packages to injected into in the environment with apps",
    )
