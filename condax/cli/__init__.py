import logging
from statistics import median
import rainbowlog
from pathlib import Path
from typing import Callable, Optional

import click

import condax.config as config
from condax import __version__


option_config = click.option(
    "--config",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    help=f"Custom path to a condax config file in YAML. Default: {config.DEFAULT_CONFIG}",
    callback=lambda _, __, f: (f and config.set_via_file(f)) or f,
)

option_channels = click.option(
    "--channel",
    "-c",
    "channels",
    multiple=True,
    help=f"""Use the channels specified to install. If not specified condax will
    default to using {config.DEFAULT_CHANNELS}, or 'channels' in the config file.""",
    callback=lambda _, __, c: (c and config.set_via_value(channels=c)) or c,
)

option_envname = click.option(
    "--name",
    "-n",
    "envname",
    required=True,
    prompt="Specify the environment (Run `condax list --short` to see available ones)",
    type=str,
    help=f"""Specify existing environment to inject into.""",
    callback=lambda _, __, n: n.strip(),
)

option_is_forcing = click.option(
    "-f",
    "--force",
    "is_forcing",
    help="""Modify existing environment and files in CONDAX_BIN_DIR.""",
    is_flag=True,
    default=False,
)


def options_logging(f: Callable) -> Callable:
    option_verbose = click.option(
        "-v",
        "--verbose",
        count=True,
        help="Raise verbosity level.",
        callback=lambda _, __, v: _LoggerSetup.set_verbose(v),
    )
    option_quiet = click.option(
        "-q",
        "--quiet",
        count=True,
        help="Decrease verbosity level.",
        callback=lambda _, __, q: _LoggerSetup.set_quiet(q),
    )
    return option_verbose(option_quiet(f))


@click.group(
    help=f"""Install and execute applications packaged by conda.

    Default variables:

      Conda environment location is {config.DEFAULT_PREFIX_DIR}\n
      Links to apps are placed in {config.DEFAULT_BIN_DIR}
    """
)
@click.version_option(
    __version__,
    message="%(prog)s %(version)s",
)
@option_config
@options_logging
def cli(**_):
    """Main entry point for condax."""
    pass


class _LoggerSetup:
    handler = logging.StreamHandler()
    formatter = rainbowlog.Formatter(logging.Formatter())
    logger = logging.getLogger((__package__ or __name__).split(".", 1)[0])
    verbose = 0
    quiet = 0

    @classmethod
    def setup(cls) -> int:
        """Setup the logger.

        Returns:
            int: The log level.
        """
        cls.handler.setFormatter(cls.formatter)
        cls.logger.addHandler(cls.handler)
        level = logging.INFO - 10 * (int(median((-1, 3, cls.verbose - cls.quiet))))
        cls.logger.setLevel(level)
        return level

    @classmethod
    def set_verbose(cls, v: int) -> int:
        """Set the verbose level and return the new log level."""
        cls.verbose += v
        return cls.setup()

    @classmethod
    def set_quiet(cls, q: int):
        """Set the quiet level and return the new log level."""
        cls.quiet += q
        return cls.setup()
