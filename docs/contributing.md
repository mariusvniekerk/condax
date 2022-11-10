# Contributing

Thanks for your interest in contributing to condax!

## Dependencies

Dependencies for condax can be installed by using any package manager you like.  For convenience [hatch](https://hatch.pypa.io/)
can be used to create a development environment

```shell
hatch env create
```

## Testing condax locally

In your environmnent run the tests as follows

```shell
hatch run check
```

## Testing condax on Github Actions

When you make a pull request, tests will automatically be run against your code as defined in `.github/workflows/pythonpackage.yml`.  These tests are run using github actions

## Documentation

`condax` autogenerates API documentation, published on github pages.

## Release New `condax` Version

To create a new release condax create a new release using github.  Artifacts will automatically be published
