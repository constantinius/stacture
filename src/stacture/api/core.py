from typing import Annotated, List
import re

from fastapi import APIRouter, Depends, HTTPException, Request

from ..source.util import get_source
from ..config import get_config
from .base import BaseAPI, LinkType
from .registry import APIRegistry, get_registry

router = APIRouter()

Config = Annotated[dict, Depends(get_config)]


@router.get("/", response_model_exclude_unset=True)
async def landing_page(request: Request, config: Config):
    registry = get_registry()
    links = []
    for api in registry.apis:
        links.extend(api.get_landing_page_links(request))

    metadata = config.get("metadata")
    return {
        "title": metadata.get("title", "stacture"),
        "description": metadata.get("description", "stacture"),
        "links": links,
    }


async def get_collection_description(
    request: Request, registry: APIRegistry, config: Config, collection_id: str
) -> dict:
    if collection_id in config["collections"]:
        collection_conf = config["collections"][collection_id]
        used_collection = collection_id
    else:
        for used_collection, collection_conf in config["collections"].items():
            if any(
                re.match(pattern, collection_id)
                for pattern in collection_conf.get("id_patterns", [])
            ):
                break
        else:
            raise HTTPException(status_code=404, detail="Item not found")

    links = []
    for api in registry.apis:
        links.extend(
            api.get_collection_links(request, collection_id, collection_conf)
        )

    source = get_source(collection_conf["source"])
    collection = await source.get_collection()

    return {
        "id": collection_id,
        "title": collection_conf.get("title", collection.title),
        "description": collection_conf.get(
            "description", collection.description
        ),
        "keywords": collection_conf.get("keywords", collection.keywords),
        "extent": collection_conf.get("extent", collection.extent),
        "links": links,
    }


@router.get("/collections")
async def collections(request: Request, config: Config):
    registry = get_registry()
    return {
        "collections": [
            await get_collection_description(request, registry, config, collection_id)
            for collection_id in config.get("collections", {}).keys()
        ],
        "links": [
            LinkType(
                href=str(request.url_for("collections")),
                rel="self",
                title="Collections",
                type="application/json",
            ).model_dump(exclude_unset=True)
        ]
    }


@router.get("/collections/{collection_id}")
async def collection(request: Request, collection_id: str, config: Config):
    registry = get_registry()
    return get_collection_description(request, registry, config, collection_id)


class CoreAPI(BaseAPI):
    def get_api_router(self) -> APIRouter:
        return router

    def get_landing_page_links(self, request: Request) -> List[LinkType]:
        return [
            LinkType(
                href=str(request.url_for("landing_page")),
                rel="self",
                title="Landing Page",
                type="application/json",
            ).model_dump(exclude_unset=True),
            # {
            #     "rel": "service-desc",
            #     "type": "application/vnd.oai.openapi+json;version=3.0",
            #     "title": "The OpenAPI definition as JSON",
            #     "href": "https://demo.pygeoapi.io/stable/openapi"
            # },
            # {
            #     "rel": "service-doc",
            #     "type": "text/html",
            #     "title": "The OpenAPI definition as HTML",
            #     "href": "https://demo.pygeoapi.io/stable/openapi?f=html",
            #     "hreflang": "en-US"
            # },
            # {
            #     "rel": "conformance",
            #     "type": "application/json",
            #     "title": "Conformance",
            #     "href": "https://demo.pygeoapi.io/stable/conformance"
            # },
            LinkType(
                href=str(request.url_for("collections")),
                rel="data",
                title="Collections",
                type="application/json",
            ).model_dump(exclude_unset=True)
        ]

    def get_collection_links(
        self, request: Request, collection_id: str, collection_conf: dict
    ) -> List[LinkType]:
        return [
            LinkType(
                href=str(request.url_for("landing_page")),
                rel="root",
                type="application/json",
            ).model_dump(exclude_unset=True),
            LinkType(
                href=str(
                    request.url_for("collection", collection_id=collection_id)
                ),
                rel="self",
                type="application/json",
            ).model_dump(exclude_unset=True),
        ]
