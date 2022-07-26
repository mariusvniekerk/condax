# condax (forked)

[![Docs](https://img.shields.io/badge/docs-mkdocs-informational)](https://mariusvniekerk.github.com/condax)
[![Licence: MIT](https://img.shields.io/github/license/mariusvniekerk/condax)](https://github.com/mariusvniekerk/condax/blob/master/LICENSE-MIT)

Condax is inspired by the excellent [pipx](https://github.com/pipxproject/pipx), and attempts to do something similar, just using conda thus lifting the constraints of only packaging python things.


## Features and differences since [`condax 0.0.5`](https://github.com/mariusvniekerk/condax/)

- Supports `condax list` to display installed packages and executables.
- Supports `condax inject` and `condax uninject` to add/remove a package to existing package environment.
    - Add executables from the injected package with `--include-apps` flag.
- Calls `mamba` internally if available.
- Supports selecting version of a package, like `condax install ipython=8.3`.
    - See [package match specifications](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications) for the detail.
- Adds command aliases:
    - `condax uninstall` is an alias of `condax remove`.
- Works as thin wrappers (bash scripts) calling `conda run` instead of symbolic links.
    - ➡️ Solves [the issue](https://github.com/mariusvniekerk/condax/issues/13) with non-Python packages
- Follows [XDG Base Directory Specification](https://stackoverflow.com/questions/1024114/location-of-ini-config-files-in-linux-unix)
    - Environments are created in `~/.local/share/condax/envs`. (Previously `~/.condax`.)
    - User configuration is loaded from `~/.config/condax/config.yaml` if exists. (Previously `~/.condaxrc`.)
- Minor bugfixes


## Known issues

This forked version relies on `conda run` internally, and there are some shortcomings:

- `ERROR conda.cli.main_run:execute` appears whenever a command yields standard error.
- Windows platform is not supported yet, though it should work on WSL/WSL2.


## Install this forked version

Use `pipx` or `pip` to install from this repository.

```
$ pipx install git+https://github.com/yamaton/condax

# or run: pip install git+https://github.com/yamaton/condax
```

## Transfer condax environments from v0.0.5

**[This instruction does not work, yet.]**

This forked version has changed the default locations of the configs and environments. If you need to keep them from the original program, please run following to transfer to the new locations.

```bash
# Move environments to new location
mkdir -p ~/.local/share/condax/envs
mv ~/.condax/* ~/.local/share/condax/envs

# If .condaxrc exists, rename to config.yaml and move to new location
[[ -f ~/.condaxrc ]] && mkdir -p ~/.config/condax && mv ~/.condaxrc ~/.config/condax/config.yaml

# Fix conda's list of environments
sed -i 's|.condax|.local/share/condax/envs|g' ~/.conda/environments.txt

# [TODO] implement `condax reinstall-all` to fix links
```
