import pathlib
import subprocess
import tempfile


Path = pathlib.Path

def test_pipx_install_roundtrip():
    """
    Install a package, then uninstall it.
    """
    from condax.core import install_package, remove_package
    import condax.config as config
    from condax.utils import to_path

    prefix_fp = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix_fp.name)
    bin_fp = tempfile.TemporaryDirectory()
    bin_dir = to_path(bin_fp.name)
    channels = ["conda-forge", "default"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    cmd = "jq"
    exe_path = bin_dir / cmd
    env_path = prefix_dir / cmd

    # Both environment and executable should be absent
    assert not exe_path.exists()
    assert not env_path.exists()

    # Both environment and executable should be created after install
    install_package(cmd)
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()

    # Should be able to execute the executable
    res = subprocess.run(f"{exe_path} --help", shell=True)
    assert res.returncode == 0

    # Both environment and executable should be gone after removal
    remove_package(cmd)
    assert not exe_path.exists()
    assert not env_path.exists()

    prefix_fp.cleanup()
    bin_fp.cleanup()


def test_install_specific_version():
    """
    Test installing a specific version of a package.
    """
    from condax.core import install_package, remove_package
    import condax.config as config
    from condax.utils import to_path

    prefix_fp = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix_fp.name)
    bin_fp = tempfile.TemporaryDirectory()
    bin_dir = to_path(bin_fp.name)
    channels = ["conda-forge", "default"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    package = "ripgrep"
    version = "12.1.1"  # older then the latest one
    package_version = f"{package}={version}"
    cmd = "rg"
    exe_path = bin_dir / cmd
    env_path = prefix_dir / package

    # Both environment and executable should be absent
    assert not exe_path.exists()
    assert not env_path.exists()

    # Both environment and executable should be created after install
    install_package(package_version)
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()

    # Should be able to execute the executable, and get the correct version
    res = subprocess.run(f"{exe_path} --version", shell=True, capture_output=True)
    assert res.stdout and (version in res.stdout.decode())
    assert res.returncode == 0

    # Both environment and executable should be gone after removal
    remove_package(package)
    assert not exe_path.exists()
    assert not env_path.exists()

    prefix_fp.cleanup()
    bin_fp.cleanup()


def test_inject_then_uninject():
    """
    Test injecting a library to an existing environment with executable, then uninject it.
    """
    from condax.core import install_package, inject_package_to, uninject_package_from
    import condax.config as config
    from condax.utils import to_path

    prefix_fp = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix_fp.name)
    bin_fp = tempfile.TemporaryDirectory()
    bin_dir = to_path(bin_fp.name)
    channels = ["conda-forge", "default"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    base = "ipython"
    injected = "numpy"
    injected_version = "1.22.4"   # older then the latest one
    injected_spec = f"{injected}={injected_version}"
    python_version = "3.9"

    exe_path = bin_dir / base
    env_path = prefix_dir / base
    injected_pkg_lib_path = prefix_dir / base / "lib" / f"python{python_version}" / "site-packages" / injected

    # None of the executable, environment, and injected package should exist
    assert not exe_path.exists()
    assert not env_path.exists()
    assert not injected_pkg_lib_path.exists()

    # Environment and executable should be created after install. But not the library to be injected.
    install_package(base)
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()
    assert not injected_pkg_lib_path.exists()

    # Make sure ipython throws error when importing numpy
    res = subprocess.run(f"{exe_path} -c 'import numpy'", shell=True, capture_output=True)
    assert res.returncode == 1
    assert "ModuleNotFoundError" in res.stdout.decode()

    # Inject python 3.9 and numpy to ipython env
    # TODO: inject both python=3.9 and numpy=1.22.4 in a single call
    inject_package_to(base, f"python={python_version}")
    inject_package_to(base, injected_spec)
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()
    assert injected_pkg_lib_path.exists() and injected_pkg_lib_path.is_dir()

    # ipython should be able to import numpy, and display the correct numpy version
    res = subprocess.run(f"{exe_path} -c 'import numpy; print(numpy.__version__)'", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout and (injected_version in res.stdout.decode())

    # the library directory should be gone after uninjecting it
    uninject_package_from(base, injected)
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()
    assert not injected_pkg_lib_path.exists()

    # Make sure ipython throws error when importing numpy ... again
    res = subprocess.run(f"{exe_path} -c 'import numpy'", shell=True, capture_output=True)
    assert res.returncode == 1
    assert "ModuleNotFoundError" in res.stdout.decode()

    prefix_fp.cleanup()
    bin_fp.cleanup()
