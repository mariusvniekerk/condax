# Condax (forked)

Condax is inspired by the excellent [pipx](https://github.com/pipxproject/pipx), and attempts to do something similar, just using [conda](https://conda.io/) instead of pip.

This allows you to install *any* application packaged with conda instead of just the ones  written in python.

## Quickstart

### Installation

```shell
> pip install git+https://github.com/yamaton/condax
> condax ensure-path
```

### Usage

Installing an app

```shell
condax install gh
gh --help
```

List installed apps

```shell
condax list
```

Removing tools

```shell
condax remove gh
```

Updating tools

```shell
condax update gh
```

Or all of them at once

```shell
condax update --all
```
