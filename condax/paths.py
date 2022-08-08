import sys
from pathlib import Path
from typing import Union

import userpath


def add_path_to_environment(path: Union[Path, str]) -> None:
    path = str(path)

    post_install_message = (
        "You likely need to open a new terminal or re-login for changes to your $PATH"
        " to take effect."
    )
    if userpath.in_current_path(path):
        print(
            f"{path} has already been added to PATH.",
            file=sys.stderr,
        )
        return

    if userpath.need_shell_restart(path):
        print(
            f"{path} has already been added to PATH. " f"{post_install_message}",
            file=sys.stderr,
        )
        return

    userpath.append(path)
    print(f"Success! Added {path} to the PATH environment variable.", file=sys.stderr)
    print(file=sys.stderr)
    print(post_install_message, file=sys.stderr)
