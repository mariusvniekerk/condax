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
    assert not exe_path.exists()

    install_package(cmd)
    assert exe_path.exists()

    res = subprocess.run(f"{exe_path} --help", shell=True)
    assert res.returncode == 0

    remove_package(cmd)
    assert not exe_path.exists()
