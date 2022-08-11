import json
from pathlib import Path
from typing import List, Optional

from condax.config import C


class _PackageBase(object):
    def __init__(self, name: str, apps: List[str], include_apps: bool):
        self.name = name
        self.apps = apps
        self.include_apps = include_apps


class MainPackage(_PackageBase):
    def __init__(self, name: str, apps: List[str], include_apps: bool = True):
        self.name = name
        self.apps = apps
        self.include_apps = True


class InjectedPackage(_PackageBase):
    pass


class CondaxMetaData(object):
    """
    Handle metadata information written in `condax_metadata.json`
    placed in each environment.
    """

    metadata_file = "condax_metadata.json"

    @classmethod
    def get_path(cls, package: str) -> Path:
        p = C.prefix_dir() / package / cls.metadata_file
        return p

    def __init__(self, main: MainPackage, injected: List[InjectedPackage] = []):
        self.main_package = main
        self.injected_packages = injected

    def inject(self, package: InjectedPackage):
        if self.injected_packages is None:
            self.injected_packages = []
        already_injected = [p.name for p in self.injected_packages]
        if package.name in already_injected:
            return
        self.injected_packages.append(package)

    def uninject(self, name: str):
        self.injected_packages = [p for p in self.injected_packages if p.name != name]

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def save(self) -> None:
        p = CondaxMetaData.get_path(self.main_package.name)
        with open(p, "w") as fo:
            fo.write(self.to_json())


def load(package: str) -> Optional[CondaxMetaData]:
    p = CondaxMetaData.get_path(package)
    if not p.exists():
        return None

    with open(p) as f:
        d = json.load(f)
        if not d:
            raise ValueError(f"Failed to read the metadata from {p}")
    return _from_dict(d)


def _from_dict(d: dict) -> CondaxMetaData:
    main = MainPackage(**d["main_package"])
    injected = [InjectedPackage(**p) for p in d["injected_packages"]]
    return CondaxMetaData(main, injected)
