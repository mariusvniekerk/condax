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
    def __init__(self, name: str, apps: List[str]):
        super().__init__(name, apps, include_apps=True)


class InjectedPackage(_PackageBase):
    pass


class CondaxMetaData(object):

    metadata_file = "condx_metadata.json"

    def __init__(self, main: MainPackage, injected: List[InjectedPackage] = []):
        self.main_package = main
        self.injected = injected

    def inject(self, package: InjectedPackage):
        if self.injected is None:
            self.injected = []
        already_injected = [p.name for p in self.injected]
        if package.name in already_injected:
            return
        self.injected.append(package)

    def uninject(self, name: str):
        self.injected = [p for p in self.injected if p.name != name]

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def save(self) -> None:
        p = C.prefix_dir() / CondaxMetaData.metadata_file
        with open(p, "w") as fo:
            fo.write(self.to_json())


def load(package: str) -> CondaxMetaData:
    p = Path(package) / CondaxMetaData.metadata_file
    with open(p) as fo:
        d = json.load(fo)
        if not d:
            raise ValueError(f"Failed to read the metadata from {p}")
    return _from_dict(d)


def _from_dict(d: dict) -> CondaxMetaData:
    main = MainPackage(**d["main_package"])
    injected = [InjectedPackage(**p) for p in d["injected"]]
    return CondaxMetaData(main, injected)
