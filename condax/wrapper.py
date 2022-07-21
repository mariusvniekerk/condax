import argparse
import pathlib
import shlex
import logging
from typing import Optional, List, Union

Path = pathlib.Path


def read_env_name(exec_path: Union[str, Path]) -> Optional[str]:
    """
    Read a condax wrapper script.

    Returns the environment name within which conda run is executed.
    """
    path = pathlib.Path(exec_path)
    exec_name = path.name
    if not path.exists():
        logging.warning(f"File missing: `{path}`.")
        return None
    if path.is_symlink():
        return None

    with open(path) as f:
        namespace = Parser.parse(f.readlines())

    if namespace is None:
        logging.warning(f"Failed to parse: `{exec_name}`.")
        return None
    elif namespace.exec_name != exec_name:
        msg = f"The wrapper `{exec_name}` is inconsistent with the target `{namespace.exec_name}`."
        logging.warning(msg)
        return None

    return namespace.prefix.name


class Parser(object):
    """
    Parser.parse(lines) parses lines to get 'conda run' information.
    """

    p = argparse.ArgumentParser()
    p_run = p.add_subparsers().add_parser("run")
    p_run.add_argument("--prefix", type=pathlib.Path)
    p_run.add_argument("exec_name")
    p_run.add_argument("args")

    @classmethod
    def _parse_args(cls, args: List[str]) -> Optional[argparse.Namespace]:
        result = None
        try:
            result = cls.p.parse_args(args)
        except AssertionError:
            pass
        return result

    @classmethod
    def _parse_line(cls, line: str) -> Optional[argparse.Namespace]:
        """
        Extract the first line executing conda/mamba run
        """
        words = shlex.split(line)
        if len(words) < 6:
            return None

        first_word = words[0]
        cmd = pathlib.Path(first_word).stem
        if cmd not in ("conda", "mamba"):
            return None

        args = words[1:]
        return cls._parse_args(args)

    @classmethod
    def parse(cls, lines: List[str]) -> Optional[argparse.Namespace]:
        for line in lines:
            result = cls._parse_line(line)
            if result is not None:
                return result
        return None
