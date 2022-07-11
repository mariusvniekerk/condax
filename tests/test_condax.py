import os
import subprocess
from shutil import which

import pytest


@pytest.fixture
def conf(tmpdir_factory, monkeypatch):
    prefix = tmpdir_factory.mktemp("prefix")
    link = tmpdir_factory.mktemp("link")

    import condax.config

    monkeypatch.setattr(condax.config, "CONDA_ENV_PREFIX_PATH", str(prefix))
    monkeypatch.setattr(condax.config, "CONDAX_LINK_DESTINATION", str(link))
    monkeypatch.setenv("PATH", str(link), prepend=os.pathsep)
    return {"prefix": str(prefix), "link": str(link)}


def test_pipx_install_roundtrip(conf):
    from condax.core import install_package, remove_package

    start = which("jq")
    assert (start is None) or (not start.startswith(conf["link"]))
    install_package("jq")
    post_install = which("jq")
    assert post_install.startswith(conf["link"])

    # ensure that the executable installed is on PATH
    subprocess.check_call(["jq", "--help"])

    # remove the env
    remove_package("jq")
    post_remove = which("jq")
    assert (post_remove is None) or (not post_remove.startswith(conf["link"]))
