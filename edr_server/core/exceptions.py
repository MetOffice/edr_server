class EdrException(Exception):
    """Base class for all Exceptions in the edr_server library"""


class InvalidEdrJsonError(EdrException):
    """
    Used when deserialising JSON into EdrModels, and whilst the JSON is valid, it doesn't conform to the EDR schemas,
    or expected elements are missing.
    """


class EdrServerImplException(EdrException):
    """Base class for exceptions relating to server endpoint implementations in `edr_server.impl`"""


class EdrCoreException(EdrException):
    """Base exception for exceptions relating to code in the `edr_server.core` modules"""


class CollectionNotFoundException(EdrCoreException):
    """
    Thrown to indicate a requested collection doesn't exist, such as in response to metadata or data queries
    that reference a collection by ID
    """
