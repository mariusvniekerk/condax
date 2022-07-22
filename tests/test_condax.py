import pathlib
import subprocess
import tempfile


Path = pathlib.Path

def test_pipx_install_roundtrip():
    from condax.core import install_package, remove_package
    import condax.config as config
    from condax.utils import to_path

    prefix = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix.name)
    binpath = tempfile.TemporaryDirectory()
    bin_dir = to_path(binpath.name)
    channels = ["conda-forge", "default"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    cmd = "jq"
    exe_path = bin_dir / cmd
    env_path = prefix_dir / cmd
    assert not exe_path.exists()
    assert not env_path.exists()

    install_package(cmd)
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()

    res = subprocess.run(f"{exe_path} --help", shell=True)
    assert res.returncode == 0

    remove_package(cmd)
    assert not exe_path.exists()
    assert not env_path.exists()


def test_install_specific_version():
    from condax.core import install_package, remove_package
    import condax.config as config
    from condax.utils import to_path

    prefix = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix.name)
    binpath = tempfile.TemporaryDirectory()
    bin_dir = to_path(binpath.name)
    channels = ["conda-forge", "default"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    package = "ripgrep"
    version = "12.1.1"
    package_version = f"{package}={version}"
    cmd = "rg"
    exe_path = bin_dir / cmd
    env_path = prefix_dir / package
    assert not exe_path.exists()
    assert not env_path.exists()

    install_package(package_version)
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()

    res = subprocess.run(f"{exe_path} --version", shell=True, capture_output=True)
    assert res.stdout and (version in res.stdout.decode())
    assert res.returncode == 0

    remove_package(package)
    assert not exe_path.exists()
    assert not env_path.exists()
