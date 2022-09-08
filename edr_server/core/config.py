import importlib
from pathlib import Path
from typing import List, Union, Type

import yaml
from yaml.loader import SafeLoader

from edr_server.core.interface import EdrDataInterface
from edr_server.core.exceptions import EdrException
from edr_server.utils.paths import app_relative_path_to_absolute


class ConfigException(EdrException):
    pass


class EdrConfig:
    """
    A site-specific configuration handler.

    Configuration options are stored in `../etc/config.yml`, which is parsed here.

    """

    def __init__(self, config_path: Union[Path, str]):
        """
        Set up site-specific configuration as defined in the config YAML file.
        Config file is relative to the root of the edr_server code
        """
        if not isinstance(config_path, Path):
            config_path = Path(config_path)

        self.yaml_path = config_path.absolute()
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

    def data_queries(self) -> List:
        """Interrogate the config to determine the types of data queries the server supports."""
        return self.yaml["server"]["capabilities"]["data_queries"]

    def collections_cache_path(self) -> Path:
        """Retrieve the path to the collections JSON file from the config YAML."""
        cjpath = Path(self.yaml["collections"]["json"]["cache_dir"])
        # If path relative, treat as relative to config file location
        cjpath = cjpath if cjpath.is_absolute() else app_relative_path_to_absolute(cjpath)
        cjpath.mkdir(parents=True, exist_ok=True)
        return cjpath

    def data_interface(self) -> EdrDataInterface:
        """
        The data interface implementation must be provided by either:
          * a named concrete implementation directory in `edr_data_interface`
            (set in `data.interface.name` in `config.yml`), or
          * an importable path to a directory containing the modules required
            by the interface that's provided by a 3rd-party data interface library;
            for example `my_data_library.edr_interface` (set in
            `data.interface.path` in `config.yml`).
        Only one of these options may be set. An error is raised in the case of both
        or neither being set.
        """
        try:
            fq_data_interface_class_name: str = self.yaml["data"]["interface"]["fully_qualified_class_name"]
        except KeyError as err:
            raise ConfigException(
                f"Looked for `data.interface.fully_qualified_class_name` in {self.yaml_path} but {err} was missing")

        try:
            data_interface_module_path, data_interface_class_name = fq_data_interface_class_name.rsplit(".", 1)
        except ValueError:
            raise ConfigException(
                f"Unable to parse `data.interface.fully_qualified_class_name. "
                f"Expected a module path using dotted notation, e.g. my_data_interface_module.MyEdrDataInterfaceClass;"
                f" `data.interface.fully_qualified_class_name` was {fq_data_interface_class_name!r}"
            )

        try:
            data_interface_module = importlib.import_module(data_interface_module_path)
        except ModuleNotFoundError:
            raise ConfigException(
                f"Unable to import {data_interface_module_path!r}; Ensure it is installed or available via PYTHONPATH")

        # noinspection PyPep8Naming
        EdrDataInterfaceImpl: Type = getattr(data_interface_module, data_interface_class_name)
        return EdrDataInterfaceImpl()


config = EdrConfig((Path(__file__).parents[2] / Path("etc/config.yml")).absolute())
