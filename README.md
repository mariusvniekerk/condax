# condax (forked)

[![Docs](https://img.shields.io/badge/docs-mkdocs-informational)](https://mariusvniekerk.github.com/condax)
[![Licence: MIT](https://img.shields.io/github/license/mariusvniekerk/condax)](https://github.com/mariusvniekerk/condax/blob/master/LICENSE-MIT)

Condax is inspired by the excellent [pipx](https://github.com/pipxproject/pipx), and attempts to do something similar, just using conda thus lifting the constraints of only packaging python things.


## New features and differences since [`condax 0.0.5`](https://github.com/mariusvniekerk/condax/)

- Supports `condax list` to display installed packages and executables.
- Supports `condax inject` and `condax uninject` to add/remove a package to existing environment.
- Use `mamba` internally if available.
- Supports specifying version of a package, like `condax install jq=1.6`.
    - See [package match specifications](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications) for the detail.
- Works as a thin wrapper using `conda run` instead of symbolic links.
    - The app installation directory is populated with scripts rather than symbolic links.
    - ➡️ Solves [the issue](https://github.com/mariusvniekerk/condax/issues/13) with non-Python packages
- Overwrites an executable wrapper if already exists in the app directory.
- Introduce `condax uninstall` as an alias of `condax remove`.
- Environments are created in `~/.local/share/condax/envs` (previously `~/.condax`)
- Condax config is read from `~/.config/condax/config.yaml` (previously `~/.condaxrc`)
- Minor bugfixes


## Install this forked version

Use `pipx` or `pip` to install from this repository.

```
$ pipx install git+https://github.com/yamaton/condax

# or run: pip install git+https://github.com/yamaton/condax
```

## Transfer condax environments from v0.0.5

**This instruction does not work.** Will update.

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
