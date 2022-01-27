import importlib
from pathlib import Path

import yaml
from yaml.loader import SafeLoader

from .paths import app_relative_path_to_absolute


class Config(object):
    """
    A site-specific configuration handler.

    Configuration options are stored in `../etc/config.yml`, which is parsed here.

    """

    def __init__(self):
        """
        Set up site-specific configuration as defined in the config YAML file.
        Config file is relative to the root of the edr_server code
        """
        self.yaml_path = app_relative_path_to_absolute("etc/config.yml")
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

    def collections_cache_path(self) -> Path:
        """Retrieve the path to the collections JSON file from the config YAML."""
        cjpath = Path(self.yaml["collections"]["json"]["cache_dir"])
        # If path relative, treat as relative to config file location
        cjpath = cjpath if cjpath.is_absolute() else app_relative_path_to_absolute(cjpath)
        cjpath.mkdir(parents=True, exist_ok=True)
        return cjpath

    def data_interface(self):
        data_interface_name = self.yaml["data"]["interface"]["name"]
        data_interface = f"edr_data_interface.concrete.{data_interface_name}"
        return importlib.import_module(data_interface)


config = Config()
