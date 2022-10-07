from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar, Generic, Set

from ._types_and_defaults import *
from ..exceptions import InvalidEdrJsonError

JsonDict = Dict[str, Any]

T = TypeVar("T", bound="EdrModel")


class EdrModel(ABC, Generic[T]):
    """
    The base class for EDR model implementations.
    It declares the standard methods for serialising to & from JSON that concrete implementations are expected to
    provide.
    """

    def __init__(self, *args, **kwargs):
        """This is here so that the signature matches what we use in the `from_json` method"""
        pass

    @classmethod
    @abstractmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        """
        Does any necessary conversion to the json dict to prep it for passing to the class' `__init__` method.
        E.g. converting nested objects.
        This method can be extended by subclasses to perform additional preparation, e.g.
        >>> # noinspection PyProtectedMember, PyShadowingNames, PyUnresolvedReferences
        >>> def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        >>>     json_dict =  super()._prepare_json_for_init(json_dict)
        >>>     # Do extra prep...
        >>>     return json_dict

        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        """
        Get valid keys for the JSON representation of this object. Used by the `from_json` method.
        Creating an abstract class method was the best option for signposting the need to implement this in subclasses.
        Python doesn't have a concept of abstract attributes (at all), and although you can have abstract properties,
        python doesn't support class-level properties, so an abstract class method is what I'm left with (without
        writing a bunch of code to create something that supports an abstract property)
        """
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_dict: JsonDict) -> T:
        """
        Create an instance of this class from an EDR compliant JSON dict

        E.g.
        >>> import json
        >>> json_str = "{...}"
        >>> my_json_dict = json.loads(json_str)
        >>> json.dumps(my_json_dict)

        Will raise an `InvalidEdrJsonError` if the provided dict has unexpected keys or otherwise can't be
        converted.
        """
        # TODO deep copy via param toggle?
        # Subclasses may need different behaviour for converting from JSON, but implementors shouldn't need to modify
        # this method. `_prepare_json_for_init` can be overridden to control how the JSON dict is converted into a form
        # that can be passed to the __init__ method, and additional keys for validation can be added to
        # `_EXPECTED_JSON_KEYS`.

        if invalid_keys := json_dict.keys() - cls._get_allowed_json_keys():  # Performs set difference.
            # The dictionary view returned by .keys() doesn't support the named set methods, but does support the set
            # operators defined in collections.abc.Set
            raise InvalidEdrJsonError(f"Unexpected keys in JSON dict: {invalid_keys!r}")

        prepared_dict = cls._prepare_json_for_init(json_dict)
        try:
            return cls(**prepared_dict)
        except Exception as exc:
            raise InvalidEdrJsonError(f"Error during conversion from JSON: {str(exc)}") from exc

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """
        Convert this object to its EDR compliant JSON dict (which can then be passed to `json.dumps()`)

        E.g.
        >>> import json
        >>> json_dict = EdrModel().to_json()
        >>> json.dumps(json_dict)
        """
        raise NotImplementedError
