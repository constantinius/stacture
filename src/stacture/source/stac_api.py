from enum import Enum
from typing import List, AsyncIterator, Optional
from urllib.parse import urljoin

import pystac
import httpx

from .base import BaseSource, Query


class HTTPMethod(Enum):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"


def get_next_link(links: List[dict]) -> Optional[dict]:
    for link in links:
        if link.get("rel") == "next":
            return link
    return None


class STACAPISource(BaseSource):
    def __init__(
        self,
        href: str,
        collection: Optional[str] = None,
        filter: Optional[dict] = None,
        method: HTTPMethod = HTTPMethod.GET,
        extra: Optional[dict] = None,
    ):
        super().__init__(extra)
        self.api_url = href
        self.collection = collection
        self.filter = filter
        self.method = method

        self._collection: Optional[pystac.Collection] = None

    async def search_items(self, query: Query) -> AsyncIterator[pystac.Item]:
        async with httpx.AsyncClient() as client:
            if self.collection:
                url = urljoin(
                    self.api_url, f"collections/{self.collection}/items"
                )
            else:
                url = urljoin(self.api_url, "search")

            params = {}
            if query.limit is not None:
                params["limit"] = query.limit

            response = await client.request(self.method.value, url, params=params)
            response.raise_for_status()

            feature_collection = response.json()

            total_count = 0
            for feature in feature_collection["features"]:
                if query.limit is not None and total_count >= query.limit:
                    break
                yield pystac.Item.from_dict(feature)
                total_count += 1

            while query.limit is not None and total_count < query.limit:
                if next_link := get_next_link(feature_collection["links"]):
                    response = await client.request(
                        next_link.get("method", "GET"),
                        next_link["href"],
                    )
                    response.raise_for_status()
                    feature_collection = response.json()

                    for feature in feature_collection["features"]:
                        if (
                            query.limit is not None
                            and total_count >= query.limit
                        ):
                            break
                        yield pystac.Item.from_dict(feature)
                        total_count += 1

    async def get_item(self, identifier: str) -> Optional[pystac.Item]:
        async with httpx.AsyncClient() as client:
            if self.collection:
                url = urljoin(
                    self.api_url, f"collections/{self.collection}/items"
                )
            else:
                url = urljoin(self.api_url, "search")

            response = await client.request(
                self.method.value, url, params={"ids": identifier}
            )
            response.raise_for_status()
            feature_collection = response.json()
            if feature_collection["features"]:
                return feature_collection["features"][0]
            return None

    async def get_collection(self) -> Optional[pystac.Collection]:
        if self.collection and not self._collection:
            async with httpx.AsyncClient() as client:
                url = urljoin(
                    self.api_url, f"collections/{self.collection}"
                )
                response = await client.get(url)
                response.raise_for_status()
                self._collection = pystac.Collection.from_dict(response.json(), url)

        return self._collection


# https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a
