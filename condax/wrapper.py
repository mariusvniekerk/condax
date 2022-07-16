import argparse
import pathlib
import shlex
import logging
from typing import Optional, List

from .config import CONDAX_LINK_DESTINATION


def read_env_name(exec_path: str) -> Optional[str]:
    """
    Read the wrapper containing 'conda run'.

    Returns the environment name within which conda run is executed.
    """
    path = pathlib.Path(exec_path)
    exec_name = path.name
    if not path.exists():
        return None

    with open(path) as f:
        p = Parser()
        namespace = p.parse(f.readlines())

    if namespace is None:
        return None
    elif namespace.exec_name != exec_name:
        logging.warning(f"The wrapper `{path}` calls `{namespace.exec_name}`.")
        return None

    return namespace.prefix.name


class Parser(object):
    def __init__(self):
        p = argparse.ArgumentParser()
        p_run = p.add_subparsers().add_parser("run")
        p_run.add_argument("--prefix", type=pathlib.Path)
        p_run.add_argument("exec_name")
        p_run.add_argument("args")
        self.p = p

    def _parse_args(self, args: List[str]) -> Optional[argparse.Namespace]:
        result = None
        try:
            result = self.p.parse_args(args)
        except AssertionError:
            pass
        return result

    def _parse_line(self, line: str) -> Optional[argparse.Namespace]:
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
        return self._parse_args(args)

    def parse(self, lines: List[str]) -> Optional[argparse.Namespace]:
        for line in lines:
            result = self._parse_line(line)
            if result is not None:
                return result
        return None
