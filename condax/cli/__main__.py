import logging
import sys
from urllib.error import HTTPError
from condax import config
from condax.exceptions import CondaxError
from .install import install
from .remove import remove, uninstall
from .update import update
from .list import run_list
from .ensure_path import ensure_path
from .inject import inject, uninject
from .export import export, run_import
from .repair import repair
from . import cli


def main():

    for subcommand in (
        install,
        remove,
        uninstall,
        update,
        run_list,
        ensure_path,
        inject,
        uninject,
        export,
        run_import,
        repair,
    ):
        cli.add_command(subcommand)

    logger = logging.getLogger(__package__)

    try:
        try:
            config.set_via_file(config.DEFAULT_CONFIG)
        except config.MissingConfigFileError:
            pass
        cli()
    except CondaxError as e:
        if e.exit_code:
            logger.error(f"Error: {e}")
        else:
            logger.info(e)
        sys.exit(e.exit_code)
    except HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        sys.exit(e.code)
    except Exception as e:
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
