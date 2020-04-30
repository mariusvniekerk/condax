## System Requirements

condax works on macOS and  linux.  Windows may be supported in future depending on user interest/.

condax does NOT need a preexisting conda installation, though if it can find one it will use it.

## Install using pip

python 3.6+ with pip is required to install condax.

Assuming you have `pip` installed for python3, run:
```
python3 -m pip install --user condax
python3 -m condax ensure-path
```

## Install using conda

Alternatively you can install condax using conda (it just feels right doing it this way).
```
conda install -c conda-forge condax
```

## Upgrade condax
```
python3 -m pip install -U condax
```

### Installation Options
condax's default binary location is `~/.local/bin`. This can be overriden using `link_destination` in `~/.condaxrc`.

condax's default conda environment location is `~/.local/condax`. This can be overriden using `prefix_path` in `~/.condaxrc`.

## Shell Completion
You can easily get your shell's tab completions working by following instructions printed with this command:
```
pipx completions
```

## Install condax Development Versions
New versions of pipx are published as beta or release candidates. These versions look something like `0.13.0b1`, where `b1` signifies the first beta release of version 0.13. These releases can be tested with
```
pip install --user pipx --upgrade --dev
```
