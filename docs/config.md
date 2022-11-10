# configuration

Condax generally requires very little configuration.

Condax will read configuration settings from a `~/.condaxrc` file, which is similar to a `.condarc` file.

This is the default state for this file.

```yaml
prefix_path: "~/.condax"
link_destination: "~/.local/bin"
channels:
    - conda-forge
    - defaults
```

Generally the only thing that most user would want to modify is to change the default channels that
are used to install libraries from.
