# What does this do?

condax works as scripts calling `conda run`. Specifically,

```bash
conda run --no-capture-output --prefix <env-directory> '<command-and-arguments>'
```

When installing a package `condax` will

* create a conda environment in `~/.local/condax/envs/PACKAGE`
* identify the binaries/executables that are installed by `PACAKGE` (not its dependencies)
* create a shell script or batch file in `~/.local/bin`
