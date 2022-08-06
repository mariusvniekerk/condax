# condax (forked)

## What is this?

`condax` is a package manager exclusively for installing commands. `condax`, built on top of `conda` variants, frees you from activating and deactivating conda environments while keeping programs in separate environments.

`condax` was originally developed by [Marius van Niekerk ](https://github.com/mariusvniekerk/condax). I'm adding features here after the version 0.0.5.


## Examples

Here is how you can install `node`. You can just execute it without activating its associated environment. `node` still lives in its own environment so there is no worry about dependencies.

```shell
condax install nodejs

# Then node is ready to run.
node --version
```

There is no magic about the operation, and you can even do the same without having `condax`; the trick is to use `conda run`. (Or `micromamba run`.)

```shell
# Create an environent `nodejs`.
mamba env create -c conda-forge -n nodejs nodejs

# Run `node --verion` within the nodejs environment.
micromamba run -n nodejs node --version
```

`condax` just creates such scripts above in your path, by default in `~/.local/bin`, and manages them together with conda environments. I guess it's quite convenient when you deal with lots of commands from conda channels. (I'm looking at you, [`bioconda`](https://bioconda.github.io/) users 🤗.)


## How to install `condax`

Use `pip` or `pipx` to install directly from this repository.

```
$ pip install git+https://github.com/yamaton/condax

# Or, pipx install git+https://github.com/yamaton/condax if pipx is available.
```


## Changes since the original [`condax 0.0.5`](https://github.com/mariusvniekerk/condax/)

- Supports `condax list` to display installed executables.
- Uses `mamba` to manipulate environments if available.
- Uses `micromamba` to run commands.
- Supports installing a package with version constraints, like `condax install ipython=8.3`.
    - See [package match specifications](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications) for the detail.
- Supports injecting/uninjecting packages onto/from an existing environment.
- Supports configuring via environment variables, or by passing a config file.
- Supports exporting and importing condax environments for reproducibility.
- Internally, this fork creates scripts calling `micromamba run` instead of creating symbolic links.
    - ➡️ Solves [the issue](https://github.com/mariusvniekerk/condax/issues/13) with non-Python packages
- Follows [XDG Base Directory Specification](https://stackoverflow.com/questions/1024114/location-of-ini-config-files-in-linux-unix) for directory and file locations:
    - Environments are created in `~/.local/share/condax/envs`. (Previously `~/.condax`.)
    - User configuration is loaded from `~/.config/condax/config.yaml` if exists. (Previously `~/.condaxrc`.)
    - Commands are exposed at `~/.local/bin` in the same manner as before.


## Known issues

- Support of Windows platform is imperfect, though it should work fine on WSL.


## Migrating environments from `condax` v0.0.5

This forked version has changed the locations of the environments and the config file. If you have already installed packages with the original `condax`, please run the following, just once, to sort out.

```bash
condax repair --migrate
```
