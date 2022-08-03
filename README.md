# condax (forked)

## What is this?

`condax` is a package manager exclusively for installing commands from conda distribution channels. `condax` frees you from activating and deactivating conda environments while keeping programs in separate environments.

`condax` was originally developed by [Marius van Niekerk ](https://github.com/mariusvniekerk/condax). I'm adding features here after the version 0.0.5.


## Examples

Here is how to install `node`, and execute it.

```shell
condax install nodejs
node --version
```

This operation is equivalent to the following; `condax` just keeps track of conda environments for commands.

```shell
conda env create -c conda-forge -n nodejs nodejs
conda run -n nodejs 'node --version'
```

## How to install `condax`

Use `pip` or `pipx` to install directly from this repository.

```
$ pip install git+https://github.com/yamaton/condax

# Or, pipx install git+https://github.com/yamaton/condax if pipx is available.
```


## Changes since the original [`condax 0.0.5`](https://github.com/mariusvniekerk/condax/)

- Supports `condax list` to display installed executables.
- Uses `mamba` internally if available.
- Supports installing a package with version constraints, like `condax install ipython=8.3`.
    - See [package match specifications](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications) for the detail.
- Supports injecting/uninjecting packages onto/from an existing environment.
- Supports configuring via environment variables, or by passing a config file.
- Supports exporting and importing conda environments (only the ones managed by `condax`).
- Internally, this fork creates scripts calling `conda run` instead of creating symbolic links.
    - ➡️ Solves [the issue](https://github.com/mariusvniekerk/condax/issues/13) with non-Python packages
- Follows [XDG Base Directory Specification](https://stackoverflow.com/questions/1024114/location-of-ini-config-files-in-linux-unix) for directory and file locations:
    - Environments are created in `~/.local/share/condax/envs`. (Previously `~/.condax`.)
    - User configuration is loaded from `~/.config/condax/config.yaml` if exists. (Previously `~/.condaxrc`.)
    - Commands are exposed at `~/.local/bin` in the same manner as before.


## Known issues

- ``ERROR conda.cli.main_run:execute(49): `conda run XXX` failed (see above for error)`` appears whenever a command returns a nonzero exit code.
- Support of Windows platform is imperfect, though it should work fine on WSL.


## Migrating environments from `condax` v0.0.5

This forked version has changed the locations of the environments and the config file. If you have already installed packages with the original `condax`, please run the following, just once, to sort out.

```bash
condax repair --migrate
```
