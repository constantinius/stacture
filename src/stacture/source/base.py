from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import AsyncIterator, Optional, Union
from dataclasses import dataclass

import pystac
from pygeofilter.ast import Node


@dataclass
class BBox:
    minx: float
    maxx: float
    miny: float
    maxy: float

    crs: Optional[str]


TimeComponent = Union[datetime, date, timedelta, None]


@dataclass
class TimeInterval:
    start: TimeComponent
    end: TimeComponent


@dataclass
class Query:
    bbox: Optional[BBox] = None
    time: Union[TimeInterval, TimeComponent] = None
    filter: Optional[Node] = None
    limit: Optional[int] = None


class BaseSource(ABC):
    def __init__(self, extra: Optional[dict] = None):
        self.extra = extra

    @abstractmethod
    async def search_items(self, query: Query) -> AsyncIterator[pystac.Item]:
        ...

    @abstractmethod
    async def get_item(self, identifier: str) -> Optional[pystac.Item]:
        ...

    @abstractmethod
    async def get_collection(self) -> Optional[pystac.Collection]:
        ...

    def extend_item(self, raw_item: dict) -> dict:
        if self.extra:
            return deepmerge(raw_item, self.extra)
        return raw_item


def deepmerge(destination: dict, source: dict) -> dict:
    """
    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            deepmerge(node, value)
        else:
            destination[key] = value

    return destination
