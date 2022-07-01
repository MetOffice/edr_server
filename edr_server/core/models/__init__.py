import abc
from typing import Any, Dict, TypeVar, Generic

from ._types_and_defaults import *

T = TypeVar("T", bound="EdrModel")


class EdrModel(abc.ABC, Generic[T]):
    """
    The base class for EDR model implementations.
    It declares the standard methods for serialising to & from JSON that concrete implementations are expected to
    provide.
    """

    @abc.abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """
        Convert this object to its EDR compliant JSON dict (which can then be passed to `json.dumps()`

        E.g.
        >>> import json
        >>> json_dict = EdrModel().to_json()
        >>> json.dumps(json_dict)
        """
        raise NotImplemented

    @classmethod
    @abc.abstractmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> T:
        """
        Create an instance of this class from an EDR compliant JSON dict

        E.g.
        >>> import json
        >>> json_str = "{...}"
        >>> my_json_dict = json.loads(json_str)
        >>> json.dumps(my_json_dict)
        """
        raise NotImplemented
