import os

import typer
import userpath


def mkpath(path):
    os.makedirs(path, exist_ok=True)


def add_path_to_environment(path):
    path = str(path)

    post_install_message = (
        "You likely need to open a new terminal or re-login for changes to your PATH"
        "to take effect."
    )
    if userpath.in_current_path(path) or userpath.need_shell_restart(path):
        if userpath.need_shell_restart(path):
            typer.secho(
                f"{path} has already been added to PATH. " f"{post_install_message}",
                err=True,
                fg=typer.colors.YELLOW,
            )
        else:
            typer.secho(
                f"{path} alread on PATH.",
                err=True,
                fg=typer.colors.YELLOW,
            )
        return

    userpath.append(path)
    typer.secho(
        f"Success! Added {path} to the PATH environment variable.",
        err=True,
        fg=typer.colors.GREEN,
    )
    typer.secho()
    typer.secho(post_install_message, err=True, fg=typer.colors.WHITE)
