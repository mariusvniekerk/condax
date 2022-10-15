import os
import subprocess
from shutil import which

import pytest


@pytest.fixture
def conf(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch):
    prefix = tmp_path_factory.mktemp("prefix")
    link = tmp_path_factory.mktemp("link")

    import condax.config

    monkeypatch.setattr(condax.config.CONFIG, "prefix_path", prefix)
    monkeypatch.setattr(condax.config.CONFIG, "link_destination", link)
    monkeypatch.setenv("PATH", str(link), prepend=os.pathsep)
    return {"prefix": str(prefix), "link": str(link)}


@pytest.fixture(scope="session", autouse=True)
def ensure_conda_executable() -> None:
    from condax.config import CONFIG

    CONFIG.ensure_conda_executable()


def test_pipx_install_roundtrip(conf):
    from condax.core import install_package, remove_package

    start = which("jq")
    assert (start is None) or (not start.startswith(conf["link"]))
    install_package("jq")

    import condax.config

    files = list(condax.config.CONFIG.link_destination.iterdir())
    print("Link Prefix:", conf["link"])
    print("Files:", files)

    post_install = which("jq", path=os.environ["PATH"])
    assert post_install is not None
    assert post_install.startswith(conf["link"])

    # ensure that the executable installed is on PATH
    subprocess.check_call(["jq", "--help"])

    # remove the env
    remove_package("jq")
    post_remove = which("jq", path=os.environ["PATH"])
    assert (post_remove is None) or (not post_remove.startswith(conf["link"]))
