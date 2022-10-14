# Contributing Guide

This guide should help you get started with contributing to the project. It will cover things such as getting your development environment setup and how to run the tests.

## Development Environment

This project uses [`hatch`](https://hatch.pypa.io/latest/) as its project management tool.

To enter the development environment (it will be created automatically) run:

```bash
$ hatch shell
```

Once in this environment you can run `condax` commands to see how your current code behaves. If you don't run `hatch shell`, you should prefix all commands mentioned below with `hatch run`.

## Running Tests

To run the tests you can use `pytest`.

```bash
$ pytest
```

## Code Formatting

This project uses `black` for code formatting and `isort` to order imports. To format your code run:

```bash
$ black .
$ isort .
```

## Type Checking

This project uses `mypy` for type checking. To run the type checker run:

```bash
$ mypy .
```

## Running Formatting and Type Checking at once

To run all of the above tools at once, you can use pre-commit.

```bash
$ pre-commit run --all-files
```

To configure it to run automatically when commiting code with git, run:

```bash
$ pre-commit install
```

If you don't do any of this, it will be run automatically anyways when you open a pull request.
