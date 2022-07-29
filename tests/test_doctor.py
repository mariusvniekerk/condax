import subprocess
import tempfile


def test_fix_links():
    """
    Test if fix_links() recovers the links correctly.
    """
    from condax.core import (
        install_package, inject_package_to,
        fix_links
    )
    import condax.config as config
    from condax.utils import to_path

    # prep
    prefix_fp = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix_fp.name)
    bin_fp = tempfile.TemporaryDirectory()
    bin_dir = to_path(bin_fp.name)
    channels = ["conda-forge"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    gh = "gh"
    injected_rg_name = "ripgrep"
    injected_rg_version = "12.1.1"  # older then the latest
    injected_rg_spec = f"{injected_rg_name}={injected_rg_version}"
    injected_rg_cmd = "rg"
    injected_xsv = "xsv"
    ipython = "ipython"
    ipython_version = "8.4.0"
    ipython_spec = f"{ipython}={ipython_version}"

    env_gh = prefix_dir / gh
    env_ipython = prefix_dir / ipython
    exe_gh = bin_dir / gh
    exe_rg = bin_dir / injected_rg_cmd
    exe_xsv = bin_dir / injected_xsv
    exe_ipython = bin_dir / ipython

    # Environment and executable should be created after install. Nothing is injected yet.
    install_package(gh)
    install_package(ipython_spec)
    inject_package_to(gh, [injected_rg_spec, injected_xsv], include_apps=True)

    # gh and ipython environment should exist
    # while there is no ripgrep environment because
    # ripgrep exists under gh environment
    assert env_gh.exists() and env_gh.is_dir()
    assert env_ipython.exists() and env_ipython.is_dir()
    assert not (prefix_dir / injected_rg_name).exists()

    # gh, rg, xsv, ipython are exposed
    assert exe_gh.exists() and exe_gh.is_file()
    assert exe_rg.exists() and exe_rg.is_file()
    assert exe_xsv.exists() and exe_xsv.is_file()
    assert exe_ipython.exists() and exe_ipython.is_file()

    # Remove wrappers in BIN_DIR
    exe_gh.unlink()
    exe_rg.unlink()
    exe_xsv.unlink()
    exe_ipython.unlink()
    assert not exe_gh.exists()
    assert not exe_rg.exists()
    assert not exe_xsv.exists()
    assert not exe_ipython.exists()

    # Recover links
    fix_links()
    assert exe_gh.exists() and exe_gh.is_file()
    assert exe_rg.exists() and exe_rg.is_file()
    assert exe_xsv.exists() and exe_xsv.is_file()
    assert exe_ipython.exists() and exe_ipython.is_file()

    # gh should be able to run, with the specified version
    res = subprocess.run(f"{exe_gh} --help", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout

    # rg (ripgrep) should be able to run
    res = subprocess.run(f"{exe_rg} --version", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout and (injected_rg_version in res.stdout.decode())

    # xsv should be able to run
    res = subprocess.run(f"{exe_xsv} --version", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout

    # ipython should be able to run, with the specified version
    res = subprocess.run(f"{exe_ipython} --version", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout and (ipython_version in res.stdout.decode())

    prefix_fp.cleanup()
    bin_fp.cleanup()



def test_fix_links_withoug_metadata():
    """
    When metadata file (condax_metadata.json) is absent,
    fix_links() should recover the links of the environments,
    but not the injected packages.
    """
    from condax.core import (
        install_package, inject_package_to,
        fix_links,
    )
    import condax.config as config
    import condax.metadata as metadata
    from condax.utils import to_path

    # prep
    prefix_fp = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix_fp.name)
    bin_fp = tempfile.TemporaryDirectory()
    bin_dir = to_path(bin_fp.name)
    channels = ["conda-forge"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    gh = "gh"
    injected_rg_name = "ripgrep"
    injected_rg_version = "12.1.1"  # older then the latest
    injected_rg_spec = f"{injected_rg_name}={injected_rg_version}"
    injected_rg_cmd = "rg"
    injected_xsv = "xsv"

    env_gh = prefix_dir / gh
    exe_gh = bin_dir / gh
    exe_rg = bin_dir / injected_rg_cmd
    exe_xsv = bin_dir / injected_xsv

    # Environment and executable should be created after install. Nothing is injected yet.
    install_package(gh)
    inject_package_to(gh, [injected_rg_spec, injected_xsv], include_apps=True)

    # gh and ipython environment should exist
    # while there is no ripgrep environment because
    # ripgrep exists under gh environment
    assert env_gh.exists() and env_gh.is_dir()
    assert not (prefix_dir / injected_rg_name).exists()

    # gh, rg, xsv, ipython are exposed
    assert exe_gh.exists() and exe_gh.is_file()
    assert exe_rg.exists() and exe_rg.is_file()
    assert exe_xsv.exists() and exe_xsv.is_file()

    # Remove wrappers in BIN_DIR
    exe_gh.unlink()
    assert not exe_gh.exists()
    assert exe_rg.exists()
    assert exe_xsv.exists()

    # Remove condax_metadata.json in gh environment
    metadata_file = prefix_dir / env_gh / metadata.CondaxMetaData.metadata_file
    assert metadata_file.exists()
    metadata_file.unlink()
    assert not metadata_file.exists()

    # Recover links without metadata
    fix_links()
    assert exe_gh.exists() and exe_gh.is_file()

    # then the wrapper executables from injected packages should be pruned away
    assert not exe_rg.exists()
    assert not exe_xsv.exists()

    # gh should be able to run
    res = subprocess.run(f"{exe_gh} --help", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout

    prefix_fp.cleanup()
    bin_fp.cleanup()
