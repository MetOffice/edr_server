import os
import yaml
from yaml import loader
from yaml.loader import SafeLoader


class Config(object):
    def __init__(self):
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
        with open(self.yaml_path, "r") as oyfh:
            self.yaml = yaml.load(oyfh, Loader=SafeLoader)

    def collections_json_path(self):
        cjpath = self.yaml["collections"]["json"]["path"]
        if cjpath.startswith("/"):
            abspath = cjpath
        else:
            abspath = os.path.abspath(cjpath)
        return abspath


config = Config()