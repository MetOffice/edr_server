from pathlib import Path
from typing import Union


def get_app_root() -> Path:
    # when a path refers to a file, the first parent is the directory containing the file.
    # Hence, the parent directory is the 2nd parent entry
    return Path(__file__).parents[1]


def app_relative_path_to_absolute(rel_path: Union[Path, str]) -> Path:
    """Converts a path that's relative to the app root directory into an absolute path"""
    return (get_app_root() / Path(rel_path)).absolute()
