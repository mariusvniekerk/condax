# List of all commands and subcommands

## `condax ensure-path`

Ensures that the path that condax installs executable links into has been added to the user's $PATH.

```
> condax ensure-path
Success! Added ~/.local/bin to the PATH environment variable.


```

## `condax install`

Installs a package with condax and add it to the user path.  

Presently only the latest version of a given package can be installed.  

```bash
> condax install PACKAGE
```

Conddax also supports using a non-standard set of channels to install a given package.  These are passed onto conda as expected

```bash
> condax install -c HIGHEST_PRIORITY_CHANNEL -c OTHER_CHANNEL -c defaults PACKAGE 
```

## `condax remove`

Removes an already installed package.  This will also remove the conda environment that was created for that package.

```bash
> condax remove PACKAGE
```

## `condax update`

This will attempt to update the environment for a given package.  In the unlikely event that this fails, you can also just remove and readd the package.

```bash
> condax update PACKAGE
```