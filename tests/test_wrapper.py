import pathlib
import textwrap

from condax.wrapper import Parser

Path = pathlib.Path

def test_read_env_name():
    script1 = textwrap.dedent("""
        #!/usr/bin/env bash

        conda run --prefix /home/user/envs/baba my-keke-exe $@

    """)
    result1 = Parser.parse(script1)
    assert result1
    assert result1.prefix == Path("/home/user/envs/baba")
    assert result1.exec_name == "my-keke-exe"
    assert result1.args == "$@"
