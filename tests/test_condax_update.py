import subprocess
import tempfile

def test_condax_update_main_apps():
    """Check if condax update main apps works correctly.
    """
    from condax.core import (
        install_package,
        update_package,
    )
    import condax.config as config
    from condax.utils import to_path, is_env_dir
    import condax.metadata as metadata

    # prep
    prefix_fp = tempfile.TemporaryDirectory()
    prefix_dir = to_path(prefix_fp.name)
    bin_fp = tempfile.TemporaryDirectory()
    bin_dir = to_path(bin_fp.name)
    channels = ["conda-forge", "bioconda"]
    config.set_via_value(prefix_dir=prefix_dir, bin_dir=bin_dir, channels=channels)

    main_pkg = "gff3toddbj"
    main_version_before_update = "0.1.1"
    main_spec_before_update = f"{main_pkg}={main_version_before_update}"
    main_version_after_update = "0.2.1"
    main_spec_after_update = f"{main_pkg}={main_version_after_update}"

    main_apps_before = {
        "gff3-to-ddbj",
        "list-products",
        "rename-ids",
        "split-fasta",
    }
    apps_before_update = {bin_dir / app for app in main_apps_before}

    main_apps_after_update = {
        "gff3-to-ddbj",
        "list-products",
        "normalize-entry-names",
        "split-fasta",
    }
    apps_after_update = {bin_dir / app for app in main_apps_after_update}

    env_dir = prefix_dir / main_pkg
    exe_main = bin_dir / "gff3-to-ddbj"

    # Before installation there should be nothing
    assert not is_env_dir(env_dir)
    assert all(not app.exists() for app in apps_before_update)

    install_package(main_spec_before_update)

    # After installtion there should be an environment and apps
    assert is_env_dir(env_dir)
    assert all(app.exists() and app.is_file() for app in apps_before_update)

    # gff3-to-ddbj --version was not implemented as of 0.1.1
    res = subprocess.run(f"{exe_main} --version", shell=True, capture_output=True)
    assert res.returncode == 2

    update_package(main_spec_after_update, update_specs=True)

    # After update there should be an environment and update apps
    assert is_env_dir(env_dir)
    assert all(app.exists() and app.is_file() for app in apps_after_update)
    to_be_removed = apps_before_update - apps_after_update

    # app named "rename-ids" should be gone after the update
    assert to_be_removed == {bin_dir / "rename-ids"}
    assert all(not app.exists() for app in to_be_removed)

    # Should get the correct version after the update
    res = subprocess.run(f"{exe_main} --version", shell=True, capture_output=True)
    assert res.returncode == 0
    assert res.stdout and (main_version_after_update in res.stdout.decode())

    meta = metadata.load(main_pkg)
    assert meta and meta.main_package and set(meta.main_package.apps) == main_apps_after_update

    prefix_fp.cleanup()
    bin_fp.cleanup()



## TODO: Add tests for update of injected packages
##
