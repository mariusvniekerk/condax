import os
import sys

from . import conda
from .config import CONDAX_LINK_DESTINATION


def install_package(package):
    conda.create_conda_environment(package)
    executables_to_link = conda.detemine_executables_from_env(package)
    for exe in executables_to_link:
        executable_name = os.path.basename(exe)
        os.symlink(exe, f"{CONDAX_LINK_DESTINATION}/{executable_name}")


def remove_package(package):
    prefix = conda.conda_env_prefix(package)
    if not os.path.exists(prefix):
        print(f"`{package}` is not installed with condax", file=sys.stderr)
        sys.exit(0)

    executables_to_link = conda.detemine_executables_from_env(package)
    for exe in executables_to_link:
        executable_name = os.path.basename(exe)
        link_name = f"{CONDAX_LINK_DESTINATION}/{executable_name}"
        if os.path.islink(link_name) and (os.readlink(link_name) == exe):
            os.unlink(link_name)
    conda.remove_conda_env(package)
