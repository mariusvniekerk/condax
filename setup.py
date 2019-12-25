#################### Maintained by Hatch ####################
# This file is auto-generated by hatch. If you'd like to customize this file
# please add your changes near the bottom marked for 'USER OVERRIDES'.
# EVERYTHING ELSE WILL BE OVERWRITTEN by hatch.
#############################################################
from io import open

from setuptools import find_packages, setup

with open("condax/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        version = "0.0.1"

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

REQUIRES = ["click", "requests", "userpath"]

setup(
    name="condax",
    version="0.0.1",
    description="Install and run applications packaged with conda in isolated environments",
    long_description=readme,
    author="Marius van Niekerk",
    author_email="marius.v.niekerk@gmail.com",
    maintainer="Marius van Niekerk",
    maintainer_email="marius.v.niekerk@gmail.com",
    url="https://github.com/mariusvniekerk/condax",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    python_requires=">=3.6",
    install_requires=REQUIRES,
    tests_require=["coverage", "pytest"],
    packages=find_packages(exclude=("tests", "tests.*")),
    entry_points={"console_scripts": ["condax = condax.cli:cli"]},
    zip_safe=True,
)
