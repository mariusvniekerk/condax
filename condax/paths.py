import logging
import sys
from pathlib import Path
from typing import Union

import userpath


logger = logging.getLogger(__name__)


def add_path_to_environment(path: Union[Path, str]) -> None:
    path = str(path)

    post_install_message = (
        "You likely need to open a new terminal or re-login for changes to your $PATH"
        " to take effect."
    )
    if userpath.in_current_path(path):
        logger.info(f"{path} has already been added to PATH.")
        return

    if userpath.need_shell_restart(path):
        logger.warning(f"{path} has already been added to PATH. {post_install_message}")
        return

    userpath.append(path)
    logger.info(f"Success! Added {path} to the PATH environment variable.\n")
    logger.info(post_install_message)
