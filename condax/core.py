import os

from .conda import create_conda_environment, detemine_executables_from_env
from .config import CONDAX_LINK_DESTINATION


def install_package(package):
    create_conda_environment(package)
    executables_to_link = detemine_executables_from_env(package)
    for exe in executables_to_link:
        executable_name = os.path.basename(exe)
        os.symlink(exe, f"{CONDAX_LINK_DESTINATION}/{executable_name}")
