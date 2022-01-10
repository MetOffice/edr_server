import os
from pathlib import Path

import yaml
from yaml.loader import SafeLoader


class Config(object):
    """
    A site-specific configuration handler.

    Configuration options are stored in `../etc/config.yml`, which is parsed here.

    """

    def __init__(self):
        """
        Set up site-specific configuration as defined in the config YAML file.
        Config file is relative to this file: ../etc/config.yml
        """
        self.yaml_path = (Path(__file__).parents[1] / Path("etc/config.yml")).absolute()
        self._yaml = None

    @property
    def yaml(self):
        if self._yaml is None:
            self.load_yaml()
        return self._yaml

    @yaml.setter
    def yaml(self, value):
        self._yaml = value

    def load_yaml(self):
        """Load the config YAML file for parsing."""
        with open(self.yaml_path, "r") as oyfh:
            self.yaml = yaml.load(oyfh, Loader=SafeLoader)

    def collections_json_path(self) -> Path:
        """Retrieve the path to the collections JSON file from the config YAML."""
        cjpath = Path(self.yaml["collections"]["json"]["path"])
        # If path relative, treat as relative to config file location
        return cjpath if cjpath.is_absolute() else (self.yaml_path.parents[1] / cjpath).absolute()


config = Config()