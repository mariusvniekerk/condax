import subprocess
import tempfile


def test_export_import():
    """
    Test exporting environments, remove all packages, then
    see if environments are recovered by importing files.
    """
    from condax.core import (
        install_package,
        inject_package_to,
        remove_package,
        export_all_environments,
        import_environments,
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

    export_dir_fp = tempfile.TemporaryDirectory()
    export_dir = to_path(export_dir_fp.name)

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
    inject_package_to(gh, [injected_rg_spec], include_apps=True)
    inject_package_to(gh, [injected_xsv])

    export_all_environments(str(export_dir))
    remove_package(gh)
    remove_package(ipython)

    assert not env_gh.exists()
    assert not env_ipython.exists()
    assert not exe_gh.exists()
    assert not exe_rg.exists()
    assert not exe_xsv.exists()
    assert (export_dir / f"{gh}.yml").exists()
    assert (export_dir / f"{gh}.json").exists()
    assert (export_dir / f"{ipython}.yml").exists()
    assert (export_dir / f"{ipython}.json").exists()

    import_environments(str(export_dir), is_forcing=False)

    # gh and ipython environment should exist
    # while there is no ripgrep environment because
    # ripgrep exists under gh environment, not under prefix_dir.
    assert env_gh.exists() and env_gh.is_dir()
    assert env_ipython.exists() and env_ipython.is_dir()
    assert not (prefix_dir / injected_rg_name).exists()

    # gh, rg, ipython are exposed
    assert exe_gh.exists() and exe_gh.is_file()
    assert exe_rg.exists() and exe_rg.is_file()
    assert exe_ipython.exists() and exe_ipython.is_file()

    # xsv is injected without --include_apps option
    # hence its executable is NOT exposed.
    assert not exe_xsv.exists()

    # gh should be able to run, with the specified version
    res = subprocess.run(f"{exe_gh} --help", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout

    # rg (ripgrep) should be able to run
    res = subprocess.run(f"{exe_rg} --version", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout and (injected_rg_version in res.stdout.decode())

    # ipython should be able to run, with the specified version
    res = subprocess.run(f"{exe_ipython} --version", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout and (ipython_version in res.stdout.decode())

    export_dir_fp.cleanup()
    prefix_fp.cleanup()
    bin_fp.cleanup()
