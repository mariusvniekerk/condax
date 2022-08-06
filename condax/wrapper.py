import argparse
import os
import pathlib
import shlex
import logging
from pathlib import Path
from typing import Optional, List, Union

from condax.utils import to_path


def read_env_name(script_path: Union[str, Path]) -> Optional[str]:
    """
    Read a condax wrapper script.

    Returns the environment name within which conda run is executed.
    """
    path = to_path(script_path)
    script_name = path.name
    if not path.exists():
        logging.warning(f"File missing: `{path}`.")
        return None
    if path.is_symlink():
        return None

    namespace = None
    try:
        with open(path) as f:
            namespace = Parser.parse(f.read())
    except UnicodeDecodeError:
        return None
    except:
        logging.warning(f"Failed in file opening and parsing: {path}")
        return None


    if namespace is None:
        logging.warning(f"Failed to parse: `{script_name}`:  {path}")
        return None
    elif namespace.exec_path.name != script_name:
        msg = f"The wrapper's {script_name} is inconsistent with the target {namespace.exec_path.name}."
        logging.warning(msg)
        return None
    elif not namespace.exec_path.exists():
        msg = f"The wrapper's exec_path {namespace.exec_path} does not exist."
        logging.warning(msg)
        return None

    return namespace.prefix.name


def is_wrapper(exec_path: Union[str, Path]) -> bool:
    """
    Check if a file is a condax wrapper script.
    """
    path = to_path(exec_path)
    if not path.exists():
        return False

    if path.is_dir() or path.is_symlink() or (not path.is_file()):
        return False

    if not (path.suffix == ".bat" or os.access(path, os.X_OK)):
        return False

    try:
        with open(path, "r", encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return False
    except:
        logging.warning(f"Something wrong with {path}")
        return False

    if "created by condax" not in content:
        return False

    return True


class Parser(object):
    """
    Parser.parse(lines) parses lines to get 'conda run' information.
    """

    p = argparse.ArgumentParser()
    p.add_argument("-p", "--prefix", type=pathlib.Path)
    p.add_argument("--no-capture-output", action="store_true")
    p.add_argument("exec_path", type=pathlib.Path)
    p.add_argument("args")

    @classmethod
    def _parse_args(cls, args: List[str]) -> Optional[argparse.Namespace]:
        try:
            result = cls.p.parse_args(args)
        except AssertionError:
            result = None
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
        cmd = to_path(first_word).stem
        if cmd not in ("conda", "mamba", "micromamba"):
            return None

        if words[1] != "run":
            return None

        args = words[2:]
        return cls._parse_args(args)

    @classmethod
    def parse(cls, text: str) -> Optional[argparse.Namespace]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            result = cls._parse_line(line)
            if result is not None:
                return result
        return None
