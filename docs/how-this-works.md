# What does this do?

condax works similarly to [pipx](https://pipxproject.github.io/pipx/how-pipx-works/).  

When installing a package condax will 

* create a conda environment in `~/.condax/PACKAGE`
* identify the binaries/executables that are installed by `PACAKGE` (not its dependencies)
* symlink those binaries to `~/.local/bin`

