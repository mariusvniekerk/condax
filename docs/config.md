Condax generally requires very little configuration.

Condax will read configuration settings from a `~/.config/condax/config.yaml` file.

This is the default state for this file.

```yaml
prefix_dir: "~/.local/share/condax/envs"
bin_dir: "~/.local/bin"
channels:
    - conda-forge
    - defaults
```

Generally the only thing that most user would want to modify is to change the default channels that
are used to install libraries from.
