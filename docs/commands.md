# List of all commands and subcommands

## `condax ensure-path`

Ensures that the path that condax installs executable links into has been added to the user's $PATH.

```shell
condax ensure-path
```

## `condax install`

Installs a package with condax and add it to the user path.

Presently only the latest version of a given package can be installed.

```shell
condax install PACKAGE
```

`condax` also supports using a non-standard set of channels to install a given package.  These are passed onto conda as expected

```shell
condax install -c HIGHEST_PRIORITY_CHANNEL -c OTHER_CHANNEL -c defaults PACKAGE
```

## `condax uninstall`

Uninstall an already installed package.  This will also remove the conda environment that was created for that package.

```shell
condax uninstall PACKAGE
```

## `condax update`

This will attempt to update the environment for a given package.  In the unlikely event that this fails, you can also just remove and readd the package.

```shell
condax update PACKAGE
```
