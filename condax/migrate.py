"""
Utilities for migrating from the original condax (version 0.0.5).

"""
import logging
import pathlib
import shutil

import condax.config as config
import condax.utils as utils


def from_old_version() -> None:
    """Migrate condax settigns from the old version to the current forked version."""
    move_condax_config()
    move_condax_envs()
    repair_conda_environment_file()


def move_condax_config() -> None:
    """Move the condax config file from ~/.condaxrc to ~/.config/condax/config.yaml"""
    from_ = pathlib.Path.home() / ".condaxrc"

    if from_.exists():
        to_ = config.DEFAULT_CONFIG
        if to_.exists():
            logging.info(
                f"A file already exists at {to_}; skipping to handle the old config file at {from_}"
            )
            return
        to_.parent.mkdir(exist_ok=True, parents=True)
        shutil.move(from_, to_)
        print(f"  [migrate] Moved {from_} to {to_}")


def move_condax_envs() -> None:
    """Move the condax envs directory from ~/.condax/ to ~/.config/condax/envs/"""
    from_ = pathlib.Path.home() / ".condax"
    if from_.exists() and from_.is_dir():
        to_ = config.C.prefix_dir()
        utils.mkdir(to_)

        for subdir in from_.iterdir():
            dst = to_ / subdir.name
            if subdir.is_dir():
                if not dst.exists():
                    shutil.move(subdir, dst)
                    print(f"  [migrate] Moved {subdir} to {dst}")
                else:
                    print(
                        f"  [migrate] Skipping {subdir} as it already exists at {dst}"
                    )


def repair_conda_environment_file() -> None:
    """Edit conda's environment file at ~/.conda/environments.txt"""
    src = pathlib.Path.home() / ".conda" / "environments.txt"
    if src.exists() and src.is_file():
        prefix_from_str = str(pathlib.Path.home() / ".condax")
        prefix_to_str = str(config.C.prefix_dir())

        with open(src, "r") as f:
            content = f.read()
        content.replace(prefix_from_str, prefix_to_str)

        backup = src.with_suffix(".bak")
        utils.unlink(backup)  # overwrite backup file if exists
        shutil.move(src, backup)

        print(f"  [migrate] Fixed paths at {src}")
        with open(src, "w") as f:
            f.write(content)
