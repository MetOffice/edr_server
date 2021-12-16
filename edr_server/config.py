import os
import yaml
from yaml.loader import SafeLoader


class Config(object):
    """
    A site-specific configuration handler.

    Configuration options are stored in `../etc/config.yml`, which is parsed here.

    """
    def __init__(self):
        """Set up site-specific configuration as defined in the config YAML file."""
        self.yaml_path = "../etc/config.yml"
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

    def collections_json_path(self):
        """Retrieve the path to the collections JSON file from the config YAML."""
        cjpath = self.yaml["collections"]["json"]["path"]
        # Handle relative paths.
        if cjpath.startswith("/"):
            abspath = cjpath
        else:
            abspath = os.path.abspath(cjpath)
        return abspath


config = Config()