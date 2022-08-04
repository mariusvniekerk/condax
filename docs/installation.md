## System Requirements

condax works on macOS and  linux.  Windows may be supported in future depending on user interest.

condax does NOT need a preexisting conda installation, though if it can find one it will use it.

## Install using pip

python 3.7+ with pip AND git is required to install condax.

Assuming you have `pip` and `git` installed, run:
```
python -m pip install --user git+https://github.com/yamaton/condax
python -m condax ensure-path
```

## Upgrade condax
```
python -m pip install -U condax
```

### Installation Options
condax's default binary location is `~/.local/bin`. This can be overriden using `bin_dir` in `~/.config/condax/config.yaml`.

condax's default conda environment location is `~/.local/condax/envs`. This can be overriden using `prefix_dir` in `~/.config/condax/config.yaml`.

