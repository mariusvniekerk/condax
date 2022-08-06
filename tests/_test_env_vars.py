from pathlib import Path
import pytest


@pytest.fixture
def mock_env_1(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CONDAX_PREFIX_DIR", "/a/s/df/ghgg")
    monkeypatch.setenv("CONDAX_BIN_DIR", "~/yuip/../.hhh/kkk")
    monkeypatch.setenv("CONDAX_CHANNELS", "fastchan  keke  baba")


# Test if C loads environment variables
def test_loading_env(mock_env_1):
    from condax.config import C
    assert C.prefix_dir() == Path("/a/s/df/ghgg")
    assert C.bin_dir() == Path.home() / ".hhh/kkk"
    assert C.channels() == ["fastchan", "keke", "baba"]



@pytest.fixture
def mock_env_2(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CONDAX_HIDE_EXITCODE", "1")


# Test if C loads to_boto_boolol variables
def test_loading_env_others(mock_env_2):
    import os
    from condax.utils import to_bool

    print(f"os.environ.get('CONDAX_HIDE_EXITCODE') = {os.environ.get('CONDAX_HIDE_EXITCODE')}")
    assert to_bool(os.environ.get("CONDAX_HIDE_EXITCODE", False))
