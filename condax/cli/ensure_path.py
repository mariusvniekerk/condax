from pathlib import Path
from typing import Optional

import condax.config as config
import condax.paths as paths
from condax import __version__

from . import cli, option_config, options_logging


@cli.command(
    help="""
    Ensure the condax links directory is on $PATH.
    """
)
@option_config
@options_logging
def ensure_path(**_):
    paths.add_path_to_environment(config.C.bin_dir())
