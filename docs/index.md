# Condax

[![Docs](https://img.shields.io/badge/docs-mkdocs-informational)](https://mariusvniekerk.github.com/condax)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/mariusvniekerk/condax/Python%20package)](https://github.com/mariusvniekerk/condax/actions?query=workflow%3A%22Python+package%22)
[![Licence: MIT](https://img.shields.io/github/license/mariusvniekerk/condax)](https://github.com/mariusvniekerk/condax/blob/master/LICENSE-MIT)
[![PyPI](https://img.shields.io/pypi/v/condax)](https://pypi.org/project/condax)
[![code-style Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://https://github.com/psf/black)


Condax is inpired by the excellent [pipx](https://github.com/pipxproject/pipx), and attempts to do something similar, just using [conda](https://conda.io/) instead of pip.

This allows you to install *any* application packaged with conda instead of just the ones  written in python.

## Quickstart

### Installation

```bash
> conda install condax
> condax ensure-path
```

### Usage

Installing tools

```bash
> condax install imagemagick
> convert some_image.png some_image.jpg
```

Removing tools

```bash
> condax remove imagemagick
```

Updating tools

```bash
> condax update imagemagick
```

Or all of them at once

```bash
> condax update --all
```
