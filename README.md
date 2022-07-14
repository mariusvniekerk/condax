# condax (forked)

[![Docs](https://img.shields.io/badge/docs-mkdocs-informational)](https://mariusvniekerk.github.com/condax)
[![Licence: MIT](https://img.shields.io/github/license/mariusvniekerk/condax)](https://github.com/mariusvniekerk/condax/blob/master/LICENSE-MIT)

Condax is inspired by the excellent [pipx](https://github.com/pipxproject/pipx), and attempts to do something similar, just using conda thus lifting the constraints of only packaging python things.


## Difference from the original [`condax`](https://github.com/mariusvniekerk/condax/)

- Supports `condax list` to display installed packages and executables.
- Works as a thin wrapper using `conda run` internally instead of symbolic links.
    - ➡️ Solves [the issue](https://github.com/mariusvniekerk/condax/issues/13) with non-Python packages
- Minor bugfixes

## Installation

```bash
$ pip install git+https://github.com/yamaton/condax
```

## License

condax is distributed under the terms of the
[MIT License](https://choosealicense.com/licenses/mit).
