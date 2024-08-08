from textwrap import dedent


def write_activating_entrypoint_unix(executable, prefix):
    dedent(
        f"""
        #!/bin/sh
        export PATH="$PATH:{prefix}/bin"

        exec "{executable}" "$@"
        """
    ).strip()


def write_activating_entrypoint_windows(executable, prefix):
    # TODO: Verify if this is right?
    dedent(
        f"""
        SET PATH="%PATH%;{prefix}\\Library\\bin;{prefix}\\Scripts"

        CALL "{executable}" "%@%"
        """
    ).strip()
