# condax (forked)

[![Docs](https://img.shields.io/badge/docs-mkdocs-informational)](https://mariusvniekerk.github.com/condax)
[![Licence: MIT](https://img.shields.io/github/license/mariusvniekerk/condax)](https://github.com/mariusvniekerk/condax/blob/master/LICENSE-MIT)

Condax is inspired by the excellent [pipx](https://github.com/pipxproject/pipx), and attempts to do something similar, just using conda thus lifting the constraints of only packaging python things.


## Difference from the original [`condax v0.0.5`](https://github.com/mariusvniekerk/condax/)

- Supports `condax list` to display installed packages and executables.
- Supports `condax inject` and `condax uninject` to add/remove a package to existing environment.
- Use `mamba` internally if available.
- Supports selecting a specifc version of a package.
    - See [package match specifications](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications) for the detail.
- Works as a thin wrapper using `conda run` instead of symbolic links.
    - The app installation directory is populated with scripts rather than symbolic links.
    - ➡️ Solves [the issue](https://github.com/mariusvniekerk/condax/issues/13) with non-Python packages
- Overwrites an executable wrapper if already exists in the app directory.
- Minor bugfixes

## Installation

Use `pipx` or `pip` to install from this repository.

```
# If you prefer pip, run this instead.
# pip install git+https://github.com/yamaton/condax

$ pipx install git+https://github.com/yamaton/condax
```

## License

condax is distributed under the terms of the
[MIT License](https://choosealicense.com/licenses/mit).
