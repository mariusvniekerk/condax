import subprocess
import tempfile


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

    # FileNotFoundError in Python 3.7
    try:
        prefix_fp.cleanup()
        bin_fp.cleanup()
    except:
        pass


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

    # FileNotFoundError in Python 3.7
    try:
        prefix_fp.cleanup()
        bin_fp.cleanup()
    except:
        pass


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
    injected_version = "1.22.4"  # older then the latest one
    injected_spec = f"{injected}={injected_version}"
    python_version = "3.9"

    exe_path = bin_dir / base
    env_path = prefix_dir / base
    injected_pkg_lib_path = (
        prefix_dir
        / base
        / "lib"
        / f"python{python_version}"
        / "site-packages"
        / injected
    )

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
    res = subprocess.run(
        f"{exe_path} -c 'import numpy'", shell=True, capture_output=True
    )
    assert res.returncode == 1
    assert "ModuleNotFoundError" in res.stdout.decode()

    # Inject python 3.9 and numpy to ipython env
    # TODO: inject both python=3.9 and numpy=1.22.4 in a single call
    inject_package_to(base, [f"python={python_version}", injected_spec])
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()
    assert injected_pkg_lib_path.exists() and injected_pkg_lib_path.is_dir()

    # ipython should be able to import numpy, and display the correct numpy version
    res = subprocess.run(
        f"{exe_path} -c 'import numpy; print(numpy.__version__)'",
        shell=True,
        capture_output=True,
    )
    assert res.returncode == 0
    assert res.stdout and (injected_version in res.stdout.decode())

    # the library directory should be gone after uninjecting it
    uninject_package_from(base, [injected])
    assert exe_path.exists() and exe_path.is_file()
    assert env_path.exists() and env_path.is_dir()
    assert not injected_pkg_lib_path.exists()

    # Make sure ipython throws error when importing numpy ... again
    res = subprocess.run(
        f"{exe_path} -c 'import numpy'", shell=True, capture_output=True
    )
    assert res.returncode == 1
    assert "ModuleNotFoundError" in res.stdout.decode()

    # FileNotFoundError in Python 3.7
    try:
        prefix_fp.cleanup()
        bin_fp.cleanup()
    except:
        pass


def test_inject_with_include_apps():
    """
    Test injecting a library to an existing environment with executable, then uninject it.
    """
    from condax.core import (
        install_package,
        inject_package_to,
        uninject_package_from,
        remove_package,
    )
    import condax.config as config
    from condax.utils import to_path

    # prep
    prefix_fp = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix_fp.name)
    bin_fp = tempfile.TemporaryDirectory()
    bin_dir = to_path(bin_fp.name)
    channels = ["conda-forge", "default"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    base_gh = "gh"
    injected_rg_name = "ripgrep"
    injected_rg_version = "12.1.1"  # older then the latest
    injected_rg_spec = f"{injected_rg_name}={injected_rg_version}"
    injected_rg_cmd = "rg"
    injected_xsv = "xsv"
    conda_meta_dir = prefix_dir / base_gh / "conda-meta"

    env_path = prefix_dir / base_gh
    exe_gh = bin_dir / base_gh
    exe_rg = bin_dir / injected_rg_cmd
    exe_xsv = bin_dir / injected_xsv

    # None of the executable, environment, and injected package should exist
    assert not exe_gh.exists()
    assert not env_path.exists()
    assert not exe_rg.exists()

    # Environment and executable should be created after install. Nothing is injected yet.
    install_package(base_gh)
    assert exe_gh.exists() and exe_gh.is_file()
    assert env_path.exists() and env_path.is_dir()
    assert not exe_rg.exists()
    assert not exe_xsv.exists()

    # Make sure gh works
    res = subprocess.run(f"{exe_gh} --help", shell=True, capture_output=True)
    assert res.returncode == 0

    # Inject ripgrep and xsv to gh env with include_apps=True
    inject_package_to(base_gh, [injected_rg_spec, injected_xsv], include_apps=True)
    assert exe_gh.exists() and exe_gh.is_file()
    assert env_path.exists() and env_path.is_dir()
    assert exe_rg.exists() and exe_rg.is_file()
    assert exe_xsv.exists() and exe_xsv.is_file()

    # rg (ripgrep) should be able to run
    res = subprocess.run(f"{exe_rg} --version", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout and (injected_rg_version in res.stdout.decode())

    # xsv (xsv) should be able to run
    res = subprocess.run(f"{exe_xsv} --version", shell=True, capture_output=True)
    assert res.returncode == 0

    # rg gets unavailable after uninjecting it
    uninject_package_from(base_gh, [injected_rg_name])
    assert exe_gh.exists() and exe_gh.is_file()
    assert env_path.exists() and env_path.is_dir()
    assert not exe_rg.exists()
    assert exe_xsv.exists() and exe_xsv.is_file()

    # Check ripgrep is gone from conda-meta
    injected_ripgrep_conda_meta = next(
        conda_meta_dir.glob(f"{injected_rg_name}-{injected_rg_version}-*.json"), None
    )
    assert injected_ripgrep_conda_meta is None

    # Check xsv still exists in conda-meta
    injected_xsv_conda_meta = next(conda_meta_dir.glob(f"{injected_xsv}-*.json"), None)
    assert injected_xsv_conda_meta is not None and injected_xsv_conda_meta.is_file()

    # Check gh, rg, and xsv are all unavailable after removing the environment
    remove_package(base_gh)
    assert not exe_gh.exists()
    assert not exe_rg.exists()
    assert not exe_xsv.exists()
    assert not env_path.exists()

    # FileNotFoundError in Python 3.7
    try:
        prefix_fp.cleanup()
        bin_fp.cleanup()
    except:
        pass
