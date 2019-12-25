Thanks for your interest in contributing to condax!

## Dependencies
Dependencies for condax can be installed by using any package manager you like.  For convenience a `environment.yaml` file 
is provided to get you set up quickly.

```
conda create env
```

## Testing condax locally
In your environmnent run the tests as follows

```
python -m pytest -vrsx .
```

## Testing condax on Github Actions
When you make a pull request, tests will automatically be run against your code as defined in `.github/workflows/pythonpackage.yml`.  These tests are run using github actions

## Creating a pull request
When making a new pull request please create a news file in the `./news` directory.  This will automatically be merged into the documentation when new releases are made.

## Documentation
`condax` autogenerates API documentation, published on github pages.

## Release New `condax` Version
To create a new release condax uses [rever](https://regro.github.io/rever-docs)

```
conda install rever
rever {new_version_number}
```
