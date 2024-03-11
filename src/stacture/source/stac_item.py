from functools import lru_cache
from typing import AsyncIterator, Optional
import httpx
import pystac

from .base import BaseSource, Query


class STACItemSource(BaseSource):
    def __init__(self, url: str):
        self.url = url

    @lru_cache
    async def _get_item(self) -> pystac.Item:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url)
            response.raise_for_status()
            return pystac.Item.from_dict(response.json())

    async def get_item(self, identifier: str) -> Optional[pystac.Item]:
        item = await self._get_item()
        return item if item.id == identifier else None

    async def get_collection(self) -> Optional[pystac.Collection]:
        return await super().get_collection()

    async def search_items(self, query: Query) -> AsyncIterator[pystac.Item]:
        # TODO: check if item matches query
        item = await self._get_item()
        yield item
