from functools import wraps
from typing import Callable, NamedTuple, Optional, Set, Type

from ows.common.types import Version


class BaseOWS:
    pass


def service(name: str, versions: Set[Version]) -> Callable[[Type[BaseOWS]], Type[BaseOWS]]:
    @wraps
    def inner(cls: Type[BaseOWS]) -> Type[BaseOWS]:
        cls._OWS_SERVICE_NAME = name
        cls._OWS_SERVICE_VERSIONS = name
        return cls
    return inner


def request(name: str, default_version: Optional[Version] = None):
    @wraps
    def inner(func: Callable) -> Callable:
        func._OWS_SERVICE_REQUEST = name
        func._OWS_DEFAULT_VERSION = default_version
        return func
    return inner
