from typing import Tuple
import re

pat = re.compile(r"<=|>=|==|!=|<|>|=")


def split_match_specs(package_with_specs: str) -> Tuple[str, str]:
    """
    Split package match specification into (<package name>, <rest>)
    https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications

    Assume the argument `package_with_specs` is unquoted.

    >>> split_match_specs("numpy=1.11")
    ("numpy", "=1.11")

    >>> split_match_specs("numpy==1.11")
    ("numpy", "==1.11")

    >>> split_match_specs("numpy>1.11")
    ("numpy", ">1.11")

    >>> split_match_specs("numpy=1.11.1|1.11.3")
    ("numpy", "=1.11.1|1.11.3")

    >>> split_match_specs("numpy>=1.8,<2")
    ("numpy", ">=1.8,<2")

    >>> split_match_specs("numpy")
    ("numpy", "")
    """
    name, *_ = pat.split(package_with_specs)
    # replace with str.removeprefix() once Python>=3.9 is assured
    match_specs = package_with_specs[
        len(name) :
    ]
    return name.strip(), match_specs.strip()
